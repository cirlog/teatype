package teaType.util;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;

import teaType.data.SynchronizedList;

/* Adapted from https://stackoverflow.com/questions/1883321/java-system-out-println-&-system-err-println-out-of-order */

/**
 * The class {@code StreamBuffer}
 * 
 * @since JDK 1.91 ~ <i>2017</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * @see teaType.data.bi.BiPrimitive
 * @see teaType.data.bi.BiDouble
 * @see teaType.data.bi.BiInteger
 * @see teaType.data.bi.BiObject
 */
public class StreamBuffer {
	static SynchronizedList<OutputStream> arr;
	static OutputStream lastStream;

	public static void fixConsole() {
		if(arr!=null) {
			return;
		}
		arr = new SynchronizedList<OutputStream>();
		System.setErr(new PrintStream(new FixedStream(System.err)));
		System.setOut(new PrintStream(new FixedStream(System.out)));
	}

	static class FixedStream extends OutputStream {
		private final OutputStream target;

		public FixedStream(OutputStream originalStream) {
			arr = null;
			lastStream = null;
			target = originalStream;
			arr.add(this);
		}

		public void write(int b) throws IOException {
			if(lastStream != this) {
				swap();
			}
			target.write(b);
		}

		public void write(byte[] b) throws IOException {
			if(lastStream != this) {
				swap();
			}
			target.write(b);
		}

		public void write(byte[] b, int off, int len) throws IOException {
			if(lastStream!=this) {
				swap();
				target.write(b, off, len);	
			}
		}

		private void swap() throws IOException {
			if(lastStream!=null) {
				lastStream.flush();
				try {
					Thread.sleep(50); // Change this integer-value to adjust the print-delay
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
			lastStream = this;
		}

		public void close() throws IOException { target.close(); }

		public void flush() throws IOException { target.flush(); }
	}
}