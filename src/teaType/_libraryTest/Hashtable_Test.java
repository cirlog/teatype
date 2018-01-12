package teaType._libraryTest;

import java.io.PrintWriter;

import teaType.data.Hashtable;

public class Hashtable_Test {
	public static void main(String[] args) {
		PrintWriter out = new PrintWriter(System.out, true);
		Hashtable h = new Hashtable(10);
		int[] a = new int[10];
		int temp;
		int c = 0;
		for(@SuppressWarnings("unused") int i : a) {
			temp = (int) (Math.random()*100);
			h.put(c, temp);
			a[c] = temp;
			c++;
		}

		out.println("Integer-Array Runtime");
		long start = System.nanoTime();
		for(int i : a) {
			out.print(i + " ");
			out.flush();
		}
		long end = System.nanoTime();
		long timeInNano = end - start;
		double timeInMillis = (double) (timeInNano * 0.000001);
		out.printf("%nTime in nanoseconds:	%d ns %nTime in milliseconds:	%f ms", timeInNano, timeInMillis);
		
		out.println("\n\nHashtable Runtime");
		start = System.nanoTime();
		for(int i = 0; i < h.getLength(); i++) {
			out.print(h.get(i) + " ");
			out.flush();
		}
		end = System.nanoTime();
		timeInNano = end - start;
		timeInMillis = (double) (timeInNano * 0.000001);
		out.printf("%nInteger-Array Runtime %nTime in nanoseconds:	%d ns %nTime in milliseconds:	%f ms", timeInNano, timeInMillis);
	}
}