package teaType.util;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;

/* Adapted from https://stackoverflow.com/questions/1883321/java-system-out-println-&-system-err-println-out-of-order */

/**
 * The class {@code StreamBuffer}
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 */
public class StreamBuffer {
	private static OutputStream lastStream = null;
	private static boolean isFixed = false;

	private static class FixedStream extends OutputStream {
		private final OutputStream target;

		public FixedStream(OutputStream originalStream) {
			target = originalStream;
		}

		@Override
		public void write(int b) throws IOException {
			if(lastStream != this) {
				swap();
			}
			target.write(b);
		}

		@Override
		public void write(byte[] b) throws IOException {
			if(lastStream != this) {
				swap();
			}
			target.write(b);
		}

		@Override
		public void write(byte[] b, int off, int len) throws IOException {
			if(lastStream != this) {
				swap();
			}
			target.write(b, off, len);
		}

		private void swap() throws IOException {
			if(lastStream != null) {
				lastStream.flush();
				try {
					Thread.sleep(50);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
			lastStream = this;
		}

		public void close() throws IOException { target.close(); }

		public void flush() throws IOException { target.flush(); }
	}
	public static void fixConsole() {
		if(isFixed) {
			return;
		}
		isFixed = true;
		System.setErr(new PrintStream(new FixedStream(System.err)));
		System.setOut(new PrintStream(new FixedStream(System.out)));
	}
}