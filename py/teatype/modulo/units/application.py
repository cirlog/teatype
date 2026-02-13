# Copyright (C) 2024-2026 Burak Günaydin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# Standard-library imports
import atexit
import os
import signal
import subprocess
import sys
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Third-party imports
from teatype.enum import EscapeColor
from teatype.io import path, shell
from teatype.logging import err, hint, log, println, success, warn, whisper
from teatype.modulo.units.backend import BackendUnit, find_available_port
from teatype.modulo.units.core import CoreUnit
from teatype.modulo.units.rax import RAXUnit
from teatype.modulo.units.service import ServiceUnit
from teatype.modulo.units.socket import SocketUnit
from teatype.comms.ipc.redis import RedisDispatch
from teatype.toolkit import dt


# Package paths for default vanilla React dashboard
PACKAGE_ROOT = Path(__file__).resolve().parents[4]
# Default React dashboard is located in ts/apps/modulo-dashboard
DEFAULT_DASHBOARD_ROOT = PACKAGE_ROOT / 'ts' / 'apps' / 'modulo-dashboard'

class ApplicationUnit(CoreUnit):
    """
    Composite powerful application unit consisting of backend, service, socket units,
    and an integrated React dashboard with logging, command dispatch, and lifecycle management.
    
    Features:
    - FastAPI backend server for API and dashboard hosting
    - Optional React dashboard dev server with Vite
    - Pluggable frontend: use vanilla Modulo dashboard or your own React app
    - Redis-based service for IPC and command handling
    - Integrated logging with history buffer
    - Graceful shutdown with signal handling
    - Built-in commands: stop, reboot, status
    
    Usage with vanilla dashboard:
        app = ApplicationUnit.create('my-app', include_dashboard=True)
        
    Usage with custom React app:
        app = ApplicationUnit.create(
            'my-app',
            include_dashboard=True,
            dashboard_root=Path('/path/to/my-react-app')
        )
    """
    
    # Log buffer for dashboard display
    _log_buffer: deque
    _log_lock: threading.Lock
    
    def __init__(self,
                 name: str,
                 *,
                 backend_host: str = '127.0.0.1',
                 backend_port: Optional[int] = None,
                 dashboard_host: str = '127.0.0.1',
                 dashboard_port: Optional[int] = None,
                 dashboard_root: Optional[Path] = None,
                 include_dashboard: bool = True,
                 include_rax: bool = True,
                 include_service: bool = True,
                 include_socket: bool = True,
                 log_buffer_size: int = 500,
                 verbose_logging: bool = True) -> None:
        """
        Initialize the ApplicationUnit with all sub-units and configuration.
        
        Args:
            name: Name of the application
            backend_host: Host for the FastAPI backend server
            backend_port: Port for the FastAPI backend server. If None, auto-finds available port starting from 8080.
            dashboard_host: Host for the React dashboard dev server
            dashboard_port: Port for the React dashboard dev server. If None, auto-finds available port starting from 5173.
            dashboard_root: Path to the React dashboard root directory.
                           If None and include_dashboard=True, uses the vanilla Modulo dashboard.
                           Set to a custom path to use your own React frontend.
            include_dashboard: Whether to enable dashboard serving and start the dev server
            include_rax: Whether to include the RAX unit
            include_service: Whether to include the Service unit
            include_socket: Whether to include the Socket unit
            log_buffer_size: Maximum number of log entries to keep in memory
            verbose_logging: Whether to print verbose startup information
        """
        super().__init__(name=name, verbose_logging=verbose_logging)
        
        # Configuration - auto-find available ports if not specified
        self.backend_host = backend_host
        self.backend_port = backend_port if backend_port is not None else find_available_port(8080)
        self.dashboard_host = dashboard_host
        # Find dashboard port starting from 5173, but skip backend port to avoid conflicts
        if dashboard_port is not None:
            self.dashboard_port = dashboard_port
        else:
            self.dashboard_port = find_available_port(5173)
        self.include_dashboard = include_dashboard
        
        # Dashboard root - use default vanilla dashboard if not specified
        self.dashboard_root = Path(dashboard_root) if dashboard_root else (DEFAULT_DASHBOARD_ROOT if include_dashboard else None)
        
        # Log buffer for dashboard
        self._log_buffer = deque(maxlen=log_buffer_size)
        self._log_lock = threading.Lock()
        self._start_time = None
        
        # Dashboard dev server process
        self._dashboard_process:Optional[subprocess.Popen] = None
        self._dashboard_thread:Optional[threading.Thread] = None
        
        # Reboot flag
        self._reboot_requested = False
        
        # Create sub-units
        self.backend = BackendUnit.create(
            name=name, 
            host=backend_host, 
            port=backend_port,
            dashboard_root=self.dashboard_root,
            verbose_logging=verbose_logging
        )
        
        self.rax = RAXUnit.create(name=name) if include_rax else None
        self.service = ServiceUnit.create(name=name, verbose_logging=verbose_logging) if include_service else None
        self.socket = SocketUnit.create(name=name) if include_socket else None
        
        # Register additional routes on the backend
        self._register_application_routes()
        
        # Register service command handlers if service is enabled
        if self.service:
            self._register_service_handlers()
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Register cleanup on exit
        atexit.register(self._cleanup)
        
    #############
    # Internals #
    #############
    
    def _register_application_routes(self) -> None:
        """
        Register additional API routes for application management.
        """
        app = self.backend._app
        
        @app.get('/api/logs', name='get_logs')
        async def get_logs(limit: int = 100) -> Dict[str, Any]:
            """
            Get recent application logs.
            """
            with self._log_lock:
                logs = list(self._log_buffer)[-limit:]
            return {
                'logs': logs,
                'total': len(self._log_buffer),
                'limit': limit
            }
        
        @app.get('/api/app/status', name='app_status')
        async def app_status() -> Dict[str, Any]:
            """
            Get comprehensive application status.
            """
            return self._get_full_status()
        
        @app.post('/api/app/command', name='dispatch_command')
        async def dispatch_command_route(command: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
            """
            Dispatch a command to the application.
            """
            return await self._handle_command(command, payload or {})
        
        @app.post('/api/app/stop', name='stop_app')
        async def stop_app_route() -> Dict[str, str]:
            """
            Stop the application gracefully.
            """
            self._add_log('INFO', 'Stop command received via API')
            # Schedule shutdown in a separate thread to allow response to be sent
            threading.Thread(target=self._delayed_shutdown, args=(0.5,), daemon=True).start()
            return {
                'status': 'shutdown_initiated', 'message': 'Application will stop shortly'
            }
        
        @app.post('/api/app/reboot', name='reboot_app')
        async def reboot_app_route() -> Dict[str, str]:
            """
            Reboot the application.
            """
            self._add_log('INFO', 'Reboot command received via API')
            self._reboot_requested = True
            threading.Thread(target=self._delayed_shutdown, args=(0.5,), daemon=True).start()
            return {
                'status': 'reboot_initiated', 'message': 'Application will reboot shortly'
            }
    
    def _register_service_handlers(self) -> None:
        """
        Register Redis command handlers on the service unit.
        """
        # Create handler functions that match the expected signature
        # The message processor matches handlers by function name to dispatch command
        
        def stop(dispatch: RedisDispatch) -> None:
            """
            Handle stop command from Redis.
            """
            whisper('Received "stop" command via Redis. Initiating shutdown ...')
            self._add_log('INFO', 'Stop command received via Redis')
            self.shutdown()
        
        def reboot(dispatch: RedisDispatch) -> None:
            """
            Handle reboot command from Redis.
            """
            whisper('Received "reboot" command via Redis. Initiating reboot ...')
            self._add_log('INFO', 'Reboot command received via Redis')
            self._reboot_requested = True
            self.shutdown()
        
        def fetch_logs(dispatch: RedisDispatch) -> None:
            """
            Handle fetch_logs command from Redis.
            """
            with self._log_lock:
                logs = list(self._log_buffer)[-100:]
            self.service.redis_service.send_response(
                original_message=dispatch,
                response_message='Logs fetched',
                payload={'logs': logs}
            )
        
        def app_status(dispatch: RedisDispatch) -> None:
            """
            Handle app_status command from Redis.
            """
            status = self._get_full_status()
            self.service.redis_service.send_response(
                original_message=dispatch,
                response_message='Status fetched',
                payload=status
            )
        
        # Register handlers on the service's message processor
        # The register_handler method takes: message_class, callable, listen_channels
        from teatype.comms.ipc.redis import RedisDispatch as RD
        processor = self.service.redis_service.message_processor
        processor.register_handler(RD, stop, None)
        processor.register_handler(RD, reboot, None)
        processor.register_handler(RD, fetch_logs, None)
        processor.register_handler(RD, app_status, None)
    
    def _setup_signal_handlers(self) -> None:
        """
        Setup signal handlers for graceful shutdown.
        """
        def signal_handler(signum, frame):
            signal_name = signal.Signals(signum).name
            self._add_log('INFO', f'Received signal {signal_name}')
            println()
            hint(f'Received {signal_name}, shutting down gracefully...', use_prefix=False)
            self.shutdown()
        
        # Register handlers for common termination signals
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)
        if hasattr(signal, 'SIGQUIT'):
            signal.signal(signal.SIGQUIT, signal_handler)
    
    def _start_dashboard_dev_server(self) -> None:
        """
        Start the React dashboard Vite dev server in background.
        """
        if not self.dashboard_root or not self.dashboard_root.exists():
            warn(f'React dashboard not found at {self.dashboard_root}. Skipping dashboard server.')
            self._add_log('WARN', 'React dashboard sources not found, skipping dev server')
            return
        
        def run_dashboard():
            try:
                # Determine pnpm command
                pnpm_cmd = 'pnpm' if shell('pnpm --version', mute=True) == 0 else 'corepack pnpm'
                
                # Start Vite dev server
                cmd = f'{pnpm_cmd} start --host {self.dashboard_host} --port {self.dashboard_port}'
                
                # Set up environment with backend port for Vite proxy configuration
                env = os.environ.copy()
                env['VITE_BACKEND_PORT'] = str(self.backend_port)
                env['VITE_DASHBOARD_PORT'] = str(self.dashboard_port)
                
                self._dashboard_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=str(self.dashboard_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    preexec_fn=os.setsid  # Create new process group for clean termination
                )
                
                self._add_log('INFO', f'Dashboard dev server started on http://{self.dashboard_host}:{self.dashboard_port}')
                
                # Read output and add to log buffer
                if self._dashboard_process.stdout:
                    for line in self._dashboard_process.stdout:
                        line = line.strip()
                        if line:
                            self._add_log('DASHBOARD', line)
                            
            except Exception as e:
                self._add_log('ERROR', f'Failed to start dashboard server: {e}')
                err(f'Failed to start dashboard dev server: {e}')
        
        self._dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        self._dashboard_thread.start()
    
    def _stop_dashboard_dev_server(self) -> None:
        """
        Stop the React dashboard Vite dev server.
        """
        if self._dashboard_process:
            try:
                # Kill the entire process group
                os.killpg(os.getpgid(self._dashboard_process.pid), signal.SIGTERM)
                self._dashboard_process.wait(timeout=5)
                self._add_log('INFO', 'Dashboard dev server stopped')
            except Exception as e:
                # Force kill if graceful termination fails
                try:
                    os.killpg(os.getpgid(self._dashboard_process.pid), signal.SIGKILL)
                except Exception:
                    pass
                self._add_log('WARN', f'Dashboard server force killed: {e}')
            finally:
                self._dashboard_process = None
    
    def _add_log(self, level: str, message: str) -> None:
        """
        Add a log entry to the buffer.
        """
        timestamp = datetime.now().isoformat()
        entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'unit': self.name
        }
        with self._log_lock:
            self._log_buffer.append(entry)
    
    def _get_full_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all application components.
        """
        uptime_seconds = 0
        if self._start_time:
            uptime_seconds = (datetime.now() - self._start_time).total_seconds()
        
        status = {
            'name': self.name,
            'designation': self.designation,
            'status': self._status or 'running',
            'uptime_seconds': uptime_seconds,
            'loop_iter': self.loop_iter,
            'backend': {
                'host': self.backend_host,
                'port': self.backend_port,
                'url': f'http://{self.backend_host}:{self.backend_port}'
            },
            'dashboard': {
                'enabled': self.include_dashboard,
                'host': self.dashboard_host,
                'port': self.dashboard_port,
                'root': str(self.dashboard_root) if self.dashboard_root else None,
                'url': f'http://{self.dashboard_host}:{self.dashboard_port}' if self.include_dashboard else None,
                'running': self._dashboard_process is not None
            },
            'service': {
                'enabled': self.service is not None,
                'connected': self.service.is_connected if self.service else False,
                'subscribed': self.service.is_subscribed if self.service else False
            } if self.service else None,
            'socket': {
                'enabled': self.socket is not None
            } if self.socket else None,
            'rax': {
                'enabled': self.rax is not None
            } if self.rax else None,
            'log_count': len(self._log_buffer)
        }
        return status
    
    async def _handle_command(self, command:str, payload:Dict) -> Dict[str,Any]:
        """
        Handle a command dispatched to the application.
        """
        self._add_log('INFO', f'Handling command: {command}')
        
        if command == 'status':
            return {'success': True, 'data': self._get_full_status()}
        elif command == 'logs':
            limit = payload.get('limit', 100)
            with self._log_lock:
                logs = list(self._log_buffer)[-limit:]
            return {'success': True, 'data': {'logs': logs}}
        elif command == 'ping':
            return {'success': True, 'data': {'pong': True, 'timestamp': datetime.now().isoformat()}}
        else:
            # Try to dispatch to service if available
            if self.service:
                try:
                    self.service.dispatch(command, receiver='all', payload=payload)
                    return {'success': True, 'data': {'dispatched': True, 'command': command}}
                except Exception as e:
                    return {'success': False, 'error': str(e)}
            return {'success': False, 'error': f'Unknown command: {command}'}
    
    def _delayed_shutdown(self, delay: float) -> None:
        """
        Shutdown after a short delay to allow API response to be sent.
        """
        time.sleep(delay)
        self.shutdown()
    
    def _cleanup(self) -> None:
        """
        Cleanup resources on exit."""
        self._stop_dashboard_dev_server()
    
    def _print_startup_banner(self) -> None:
        """
        Print startup banner with clickable URLs.
        """
        println()
        log(f'{EscapeColor.GREEN}╔══════════════════════════════════════════════════════════╗{EscapeColor.RESET}')
        log(f'{EscapeColor.GREEN}║{EscapeColor.RESET}  {EscapeColor.CYAN}TeaType Modulo Application Unit Started{EscapeColor.RESET}                 {EscapeColor.GREEN}║{EscapeColor.RESET}')
        log(f'{EscapeColor.GREEN}╠══════════════════════════════════════════════════════════╣{EscapeColor.RESET}')
        log(f'{EscapeColor.GREEN}║{EscapeColor.RESET}  {EscapeColor.MAGENTA}Application:{EscapeColor.RESET} {self.name:<43} {EscapeColor.GREEN}║{EscapeColor.RESET}')
        log(f'{EscapeColor.GREEN}╠══════════════════════════════════════════════════════════╣{EscapeColor.RESET}')
        
        # Backend URL - clickable in most terminals
        backend_url = f'http://{self.backend_host}:{self.backend_port}'
        log(f'{EscapeColor.GREEN}║{EscapeColor.RESET}  {EscapeColor.YELLOW}Backend API:{EscapeColor.RESET}     {EscapeColor.BLUE}{backend_url:<35}{EscapeColor.RESET} {EscapeColor.GREEN}║{EscapeColor.RESET}')
        
        # Dashboard URL - clickable in most terminals
        dashboard_url = f'http://{self.backend_host}:{self.backend_port}/dashboard'
        log(f'{EscapeColor.GREEN}║{EscapeColor.RESET}  {EscapeColor.YELLOW}Dashboard:{EscapeColor.RESET}       {EscapeColor.BLUE}{dashboard_url:<35}{EscapeColor.RESET} {EscapeColor.GREEN}║{EscapeColor.RESET}')
        
        # Vite dev server URL if enabled
        if self.include_dashboard:
            vite_url = f'http://{self.dashboard_host}:{self.dashboard_port}'
            log(f'{EscapeColor.GREEN}║{EscapeColor.RESET}  {EscapeColor.YELLOW}Vite Dev:{EscapeColor.RESET}        {EscapeColor.BLUE}{vite_url:<35}{EscapeColor.RESET} {EscapeColor.GREEN}║{EscapeColor.RESET}')
        
        log(f'{EscapeColor.GREEN}╠══════════════════════════════════════════════════════════╣{EscapeColor.RESET}')
        log(f'{EscapeColor.GREEN}║{EscapeColor.RESET}  {EscapeColor.WHITE}Press Ctrl+C to stop{EscapeColor.RESET}                                    {EscapeColor.GREEN}║{EscapeColor.RESET}')
        log(f'{EscapeColor.GREEN}╚══════════════════════════════════════════════════════════╝{EscapeColor.RESET}')
        println()
    
    ##############
    # Public API #
    ##############

    def start(self) -> None:
        """
        Start all application components.
        """
        self._start_time = datetime.now()
        self._add_log('INFO', 'Application starting')
        
        # Print startup banner with URLs
        self._print_startup_banner()
        
        # Start dashboard dev server if enabled
        if self.include_dashboard:
            self._start_dashboard_dev_server()
        
        # Start backend and service threads
        self.backend.start()
        
        if self.socket:
            self.socket.start()
            
        if self.service:
            self.service.start()
        
        self._add_log('INFO', 'All components started')
        success('All application components started', include_symbol=True)
    
    def join(self) -> None:
        """
        Wait for all components to finish.
        """
        self.backend.join()
        
        if self.socket:
            self.socket.join()
            
        if self.service:
            self.service.join()
    
    def shutdown(self, force: bool = False) -> None:
        """
        Gracefully shutdown all application components.
        """
        if not force and self._shutdown_in_progress:
            return
        
        self._shutdown_in_progress = True
        self._add_log('INFO', 'Shutdown initiated')
        hint('Shutting down application...', pad_before=1)
        
        # Stop dashboard dev server
        self._stop_dashboard_dev_server()
        
        # Shutdown backend
        if hasattr(self.backend, 'shutdown'):
            self.backend.shutdown()
        
        # Shutdown socket
        if self.socket and hasattr(self.socket, 'shutdown'):
            self.socket.shutdown()
        
        # Shutdown service (this will close Redis connection)
        if self.service:
            self.service._terminate_redis_connection()
            if hasattr(self.service, 'shutdown'):
                self.service.shutdown()
        
        self._add_log('INFO', 'Shutdown complete')
        success('Application shutdown complete', include_symbol=True)
        
        # Handle reboot if requested
        if self._reboot_requested:
            hint('Reboot requested, restarting application...', pad_before=1)
            self._add_log('INFO', 'Rebooting application')
            # Re-execute the current script
            python = sys.executable
            os.execl(python, python, *sys.argv)
    
    def broadcast_message(self, *args, **kwargs) -> None:
        """
        Broadcast a message via the service unit.
        """
        if self.service:
            return self.service.broadcast(*args, **kwargs)
        warn('Service unit not enabled, cannot broadcast message')
    
    def dispatch_command(self, *args, **kwargs) -> None:
        """
        Dispatch a command via the service unit.
        """
        if self.service:
            return self.service.dispatch(*args, **kwargs)
        warn('Service unit not enabled, cannot dispatch command')