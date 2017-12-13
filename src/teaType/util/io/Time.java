package teaType.util.io;

import teaType.util.StreamBuffer;

public class Time {
	long start, stop, time;
	final double MIL = Math.pow(10, -6), SEC = Math.pow(10, -9), MIN = Math.pow(10, -11);

	public Time() {
		start = stop = time = 0;
	}

	public final void start() { start = System.nanoTime(); }

	public final void stop() {
		stop = System.nanoTime();
		time = stop - start;
	}

	public final String retrieve() { return time + ""; }

	public final void print(boolean milli, boolean sec, boolean min) {
		StreamBuffer.fixConsole();
		System.err.print("Nano-seconds: ");
		System.out.printf("%d ns", time);
		if(milli) {
			System.err.print(" | Milliseconds: ");
			System.out.printf("%d ms", (long) (time*MIL));
		}
		if(sec) {
			System.err.print(" | Seconds: ");
			System.out.printf("%.2f", time*SEC);
		}
		if(min) {
			System.err.print(" | Minutes: ");
			System.out.printf("%f", (time*MIL / (1000*60)) % 60);
		}
	}
	
	public final void println(boolean milli, boolean sec, boolean min) {
		print(milli, sec, min);
		System.out.println();
	}

	public final void run(int ms) {
	}
}