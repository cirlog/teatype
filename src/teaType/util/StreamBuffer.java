package teaType.util;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;

import java.util.ArrayList;
import java.util.List;

public class StreamBuffer {
	private static List<OutputStream> streams = null;
	private static OutputStream lastStream = null;

	private static class FixedStream extends OutputStream {

		private final OutputStream target;

		public FixedStream(OutputStream originalStream) {
			target = originalStream;
			streams.add(this);
		}

		public void write(int b) throws IOException {
			if (lastStream != this) {
				swap();
			}
			target.write(b);
		}

		public void write(byte[] b) throws IOException {
			if (lastStream != this) {
				swap();
			}
			target.write(b);
		}

		public void write(byte[] b, int off, int len) throws IOException {
			if (lastStream!=this) swap();
			target.write(b, off, len);
		}

		private void swap() throws IOException {
			if (lastStream!=null) {
				lastStream.flush();
				try {
					Thread.sleep(50); // Change this value to adjust the print-delay
				} catch (InterruptedException e) {

				}
			}
			lastStream = this;
		}

		public void close() throws IOException {
			target.close();
		}
		public void flush() throws IOException {
			target.flush();
		}
	}

	public static void fixConsole() {
		if (streams!=null) {
			return;
		}
		streams = new ArrayList<OutputStream>();
		System.setErr(new PrintStream(new FixedStream(System.err)));
		System.setOut(new PrintStream(new FixedStream(System.out)));
	}
}