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

"""
Test script for Redis request-response functionality.

This script tests:
1. Automatic response when await_response=True is set
2. Manual response sending via send_response()
3. Response timeout handling
4. Dispatch and Broadcast messages with response requests

Requirements:
- Redis server must be running on localhost:6379
"""

# Standard-library imports
import threading
import time
from pprint import pprint

# Third-party imports
import pytest

from teatype.comms.ipc.redis import (
    RedisServiceManager,
    RedisChannel,
    RedisBroadcast,
    RedisDispatch,
    RedisResponse,
    dispatch_handler,
    message_handler
)
from teatype.logging import *


class TestReceiverService:
    """
    A test service that receives and handles Redis messages.
    Handlers are auto-wired via the @dispatch_handler and @message_handler decorators.
    """
    service:RedisServiceManager
    received_dispatches:list
    received_broadcasts:list
    
    def __init__(self):
        self.received_dispatches = []
        self.received_broadcasts = []
        self.service = RedisServiceManager(
            client_name='test_receiver',
            channels=[RedisChannel.COMMANDS, RedisChannel.NOTIFICATIONS],
            owner=self,
            verbose_logging=True
        )
    
    @dispatch_handler
    def process_data(self, dispatch:object):
        """Handle process_data dispatch command."""
        log(f'[Receiver] Received dispatch command: {dispatch.command}')
        log(f'[Receiver] Payload: {dispatch.payload}')
        self.received_dispatches.append(dispatch)
        # Return value becomes response message if it's a string,
        # otherwise becomes response payload
        return f'Processed data: {dispatch.payload}'
    
    @dispatch_handler  
    def compute_sum(self, dispatch:object):
        """Handle compute_sum dispatch command - returns payload instead of string."""
        log(f'[Receiver] Computing sum for: {dispatch.payload}')
        self.received_dispatches.append(dispatch)
        numbers = dispatch.payload.get('numbers', [])
        result = sum(numbers)
        # Return dict payload
        return {'result': result, 'count': len(numbers)}
    
    @message_handler(RedisBroadcast, listen_channels=[RedisChannel.NOTIFICATIONS.value])
    def handle_notification(self, message:object):
        """Handle broadcast notifications."""
        log(f'[Receiver] Received broadcast: {message.message}')
        self.received_broadcasts.append(message)
        return 'Notification acknowledged'
    
    def terminate(self):
        self.service.terminate()


class TestSenderService:
    """
    A test service that sends Redis messages and awaits responses.
    """
    service:RedisServiceManager
    
    def __init__(self):
        self.service = RedisServiceManager(
            client_name='test_sender',
            channels=[RedisChannel.COMMANDS, RedisChannel.NOTIFICATIONS],
            verbose_logging=True
        )
    
    def terminate(self):
        self.service.terminate()


# ====================
# Pytest Test Cases
# ====================

@pytest.fixture
def receiver_service():
    """Create and yield a receiver service, then cleanup."""
    service = TestReceiverService()
    time.sleep(0.5)  # Allow service to initialize
    yield service
    service.terminate()


@pytest.fixture
def sender_service():
    """Create and yield a sender service, then cleanup."""
    service = TestSenderService()
    time.sleep(0.5)  # Allow service to initialize
    yield service
    service.terminate()


@pytest.mark.integration
def test_dispatch_with_await_response(receiver_service, sender_service):
    """Test dispatch message with automatic response awaiting."""
    # Create dispatch message
    dispatch = RedisDispatch(
        channel=RedisChannel.COMMANDS.value,
        source='test_sender',
        command='process_data',
        receiver='test_receiver',
        payload={'data': 'test_value', 'id': 123}
    )
    
    # Send with await_response=True
    response = sender_service.service.send_message(
        dispatch,
        await_response=True,
        response_timeout=5.0
    )
    
    # Verify response received
    assert response is not None, "Should receive a response"
    assert isinstance(response, RedisResponse), "Response should be RedisResponse"
    assert response.response_to == dispatch.id, "Response should reference original message ID"
    assert 'Processed data' in response.response_message, "Response message should contain handler result"
    
    log(f'[Test] Response received: {response.response_message}')
    log(f'[Test] Response ID linked to: {response.response_to}')


@pytest.mark.integration
def test_dispatch_with_payload_response(receiver_service, sender_service):
    """Test dispatch that returns a payload (dict) in the response."""
    dispatch = RedisDispatch(
        channel=RedisChannel.COMMANDS.value,
        source='test_sender',
        command='compute_sum',
        receiver='test_receiver',
        payload={'numbers': [1, 2, 3, 4, 5]}
    )
    
    response = sender_service.service.send_message(
        dispatch,
        await_response=True,
        response_timeout=5.0
    )
    
    assert response is not None, "Should receive a response"
    assert response.payload is not None, "Response should have payload"
    assert response.payload.get('result') == 15, "Sum should be 15"
    assert response.payload.get('count') == 5, "Count should be 5"
    
    log(f'[Test] Payload response: {response.payload}')


@pytest.mark.integration
def test_broadcast_with_await_response(receiver_service, sender_service):
    """Test broadcast message with automatic response awaiting."""
    broadcast = RedisBroadcast(
        channel=RedisChannel.NOTIFICATIONS.value,
        source='test_sender',
        message='System alert: Test notification',
        value={'severity': 'info'}
    )
    
    response = sender_service.service.send_message(
        broadcast,
        await_response=True,
        response_timeout=5.0
    )
    
    assert response is not None, "Should receive a response"
    assert response.response_to == broadcast.id, "Response should reference original message ID"
    assert 'acknowledged' in response.response_message.lower(), "Response should acknowledge"
    
    log(f'[Test] Broadcast response: {response.response_message}')


@pytest.mark.integration
def test_dispatch_without_await_response(receiver_service, sender_service):
    """Test that dispatch without await_response returns immediately."""
    dispatch = RedisDispatch(
        channel=RedisChannel.COMMANDS.value,
        source='test_sender',
        command='process_data',
        receiver='test_receiver',
        payload={'fire_and_forget': True}
    )
    
    start_time = time.time()
    response = sender_service.service.send_message(dispatch, await_response=False)
    elapsed = time.time() - start_time
    
    assert response is None, "Should return None when not awaiting"
    assert elapsed < 0.5, "Should return almost immediately"
    
    # Give time for message to be processed
    time.sleep(0.5)
    
    # Verify receiver still got the message
    assert len(receiver_service.received_dispatches) > 0, "Receiver should have gotten the dispatch"
    
    log(f'[Test] Fire-and-forget completed in {elapsed:.3f}s')


@pytest.mark.integration
def test_response_timeout(sender_service):
    """Test that timeout works when no handler exists for the command."""
    # Send to a command that has no handler
    dispatch = RedisDispatch(
        channel=RedisChannel.COMMANDS.value,
        source='test_sender',
        command='nonexistent_command',
        receiver='nobody',
        payload={}
    )
    
    start_time = time.time()
    response = sender_service.service.send_message(
        dispatch,
        await_response=True,
        response_timeout=1.0  # Short timeout
    )
    elapsed = time.time() - start_time
    
    assert response is None, "Should return None on timeout"
    assert 0.9 < elapsed < 1.5, f"Should timeout around 1 second, got {elapsed:.2f}s"
    
    log(f'[Test] Timeout test completed in {elapsed:.2f}s')


@pytest.mark.integration
def test_manual_response(receiver_service, sender_service):
    """Test manual response sending via send_response()."""
    received_message = None
    response_received = threading.Event()
    
    # Register a custom handler that stores the message for manual response
    def manual_handler(message:RedisBroadcast):
        nonlocal received_message
        received_message = message
        log(f'[Receiver] Got message for manual response: {message.message}')
        # Don't return anything - we'll send manual response
    
    # Register handler manually
    receiver_service.service.message_processor.register_handler(
        message_class=RedisBroadcast,
        callable=manual_handler,
        listen_channels=[RedisChannel.ALERTS.value]
    )
    
    # Subscribe to alerts channel
    receiver_service.service.pool.subscribe_channels([RedisChannel.ALERTS])
    sender_service.service.pool.subscribe_channels([RedisChannel.ALERTS])
    time.sleep(0.3)
    
    # Send broadcast without expecting auto-response
    broadcast = RedisBroadcast(
        channel=RedisChannel.ALERTS.value,
        source='test_sender',
        message='Manual response test',
        value={'test': True},
        response_requested=False  # No auto-response
    )
    
    sender_service.service.send_message(broadcast, await_response=False)
    time.sleep(0.5)  # Wait for message to be received
    
    # Now send manual response
    assert received_message is not None, "Should have received the message"
    
    success = receiver_service.service.send_response(
        original_message=received_message,
        response_message='Manual response sent!',
        payload={'manual': True, 'timestamp': time.time()}
    )
    
    assert success, "Manual response should be sent successfully"
    log('[Test] Manual response sent successfully')


# ====================
# Standalone Test Runner
# ====================

def run_standalone_tests():
    """
    Run tests standalone (without pytest) for quick manual testing.
    Requires Redis server to be running.
    """
    print("=" * 60)
    print("Redis Request-Response Test Suite")
    print("=" * 60)
    print()
    
    receiver = None
    sender = None
    
    try:
        # Initialize services
        print("[Setup] Creating receiver service...")
        receiver = TestReceiverService()
        time.sleep(0.5)
        
        print("[Setup] Creating sender service...")
        sender = TestSenderService()
        time.sleep(0.5)
        
        print()
        print("-" * 40)
        print("Test 1: Dispatch with await_response")
        print("-" * 40)
        
        dispatch = RedisDispatch(
            channel=RedisChannel.COMMANDS.value,
            source='test_sender',
            command='process_data',
            receiver='test_receiver',
            payload={'data': 'hello_world', 'count': 42}
        )
        
        print(f"[Sender] Sending dispatch (ID: {dispatch.id})...")
        response = sender.service.send_message(
            dispatch,
            await_response=True,
            response_timeout=5.0
        )
        
        if response:
            print(f"[Sender] ✓ Response received!")
            print(f"         - Response ID: {response.id}")
            print(f"         - Response to: {response.response_to}")
            print(f"         - Message: {response.response_message}")
            print(f"         - Payload: {response.payload}")
        else:
            print("[Sender] ✗ No response received (timeout)")
        
        print()
        print("-" * 40)
        print("Test 2: Dispatch with payload response")
        print("-" * 40)
        
        dispatch2 = RedisDispatch(
            channel=RedisChannel.COMMANDS.value,
            source='test_sender',
            command='compute_sum',
            receiver='test_receiver',
            payload={'numbers': [10, 20, 30, 40]}
        )
        
        print(f"[Sender] Sending compute_sum dispatch...")
        response2 = sender.service.send_message(
            dispatch2,
            await_response=True,
            response_timeout=5.0
        )
        
        if response2:
            print(f"[Sender] ✓ Response received!")
            print(f"         - Payload: {response2.payload}")
        else:
            print("[Sender] ✗ No response received (timeout)")
        
        print()
        print("-" * 40)
        print("Test 3: Broadcast with await_response")
        print("-" * 40)
        
        broadcast = RedisBroadcast(
            channel=RedisChannel.NOTIFICATIONS.value,
            source='test_sender',
            message='Test broadcast notification',
            value={'priority': 'high'}
        )
        
        print(f"[Sender] Sending broadcast (ID: {broadcast.id})...")
        response3 = sender.service.send_message(
            broadcast,
            await_response=True,
            response_timeout=5.0
        )
        
        if response3:
            print(f"[Sender] ✓ Response received!")
            print(f"         - Message: {response3.response_message}")
        else:
            print("[Sender] ✗ No response received (timeout)")
        
        print()
        print("-" * 40)
        print("Test 4: Fire-and-forget (no await)")
        print("-" * 40)
        
        dispatch3 = RedisDispatch(
            channel=RedisChannel.COMMANDS.value,
            source='test_sender',
            command='process_data',
            receiver='test_receiver',
            payload={'async': True}
        )
        
        print(f"[Sender] Sending fire-and-forget dispatch...")
        start = time.time()
        result = sender.service.send_message(dispatch3, await_response=False)
        elapsed = time.time() - start
        
        print(f"[Sender] ✓ Returned in {elapsed*1000:.1f}ms (result: {result})")
        time.sleep(0.3)
        print(f"[Receiver] Dispatches received: {len(receiver.received_dispatches)}")
        
        print()
        print("-" * 40)
        print("Test 5: Timeout test (no handler)")
        print("-" * 40)
        
        dispatch4 = RedisDispatch(
            channel=RedisChannel.COMMANDS.value,
            source='test_sender',
            command='nonexistent_handler',
            receiver='nobody',
            payload={}
        )
        
        print(f"[Sender] Sending to nonexistent handler (1s timeout)...")
        start = time.time()
        response4 = sender.service.send_message(
            dispatch4,
            await_response=True,
            response_timeout=1.0
        )
        elapsed = time.time() - start
        
        if response4 is None:
            print(f"[Sender] ✓ Correctly timed out after {elapsed:.2f}s")
        else:
            print(f"[Sender] ✗ Unexpectedly received response")
        
        print()
        print("-" * 40)
        print("Test 6: Manual response")
        print("-" * 40)
        
        # We'll use the already-received dispatch for manual response demo
        if len(receiver.received_dispatches) > 0:
            original = receiver.received_dispatches[0]
            print(f"[Receiver] Sending manual response to message {original.id}...")
            
            success = receiver.service.send_response(
                original_message=original,
                response_message='This is a manually sent response',
                payload={'manual': True, 'extra_data': 'some_value'}
            )
            
            if success:
                print("[Receiver] ✓ Manual response sent successfully")
            else:
                print("[Receiver] ✗ Failed to send manual response")
        
        print()
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except ConnectionError as e:
        print(f"\n[Error] Could not connect to Redis: {e}")
        print("Make sure Redis server is running on localhost:6379")
    except Exception as e:
        print(f"\n[Error] Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[Cleanup] Terminating services...")
        if sender:
            sender.terminate()
        if receiver:
            receiver.terminate()
        print("[Cleanup] Done")


if __name__ == '__main__':
    run_standalone_tests()
