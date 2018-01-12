package teaType._libraryTest;

import java.io.PrintWriter;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.LinkedList;

import teaType.util.rigid.Random;

public class Randomizer_Test {
	private static long[] time;
	
	public static void main(String[] args) {
		PrintWriter out = new PrintWriter(System.out, true);
		
		time = new long[3];
		for(int i = 0; i < 100; i++) {
			out.println(new Random().nextInt(2));
		}
		//speedTest_printInteger(out);
	}

	private final static void speedTest_printInteger(PrintWriter out) {
		int[] temp = Random.generateInteger(100000, 0, true, true, false);
		int[] arr = new int[temp.length];
		LinkedList<Integer> linkList = new LinkedList<Integer>();
		ArrayList<Integer> arrList = new ArrayList<Integer>();
		Hashtable<Integer, Integer> ht = new Hashtable<Integer, Integer>();
		HashMap<Integer, Integer> hm = new HashMap<Integer, Integer>();
		int count = 0;
		for(int i : temp) {
			arr[count] = i;
			linkList.add(i);
			arrList.add(i);
			ht.put(i, i);
			hm.put(i, i);
			count++;
		}

		///////////////////////////////////////////////////////////////////////
		// Print Speed | Integer-Array
		startTime();
		for(int i = 0; i < arr.length; i++) {
			out.print(arr[i]);
		}
		out.println();
		stopTime();
		printResult("Writing Speed", "Integer-Array");

		///////////////////////////////////////////////////////////////////////
		// Print Speed | LinkedList
		startTime();
		for(int i = 0; i < linkList.size(); i++) {
			out.print(linkList.get(i));
		}
		out.println();
		stopTime();
		printResult("Writing Speed", "Integer-LinkedList");
		
		///////////////////////////////////////////////////////////////////////
		// Print Speed | Array-List
		
		///////////////////////////////////////////////////////////////////////
		// Print Speed | Hashtable
		
		///////////////////////////////////////////////////////////////////////
		// Print Speed | HashMap
		
	}
	
	private static final void startTime() {
		time[0] = System.nanoTime();
	}
	
	private static final void stopTime() {
		time[1] = System.nanoTime();
		time[2] = time[1] - time[0];
	}

	private static final void printResult(String action, String datatype) {
		double time = (double) (Randomizer_Test.time[2]);
		System.out.printf("%s | %s: %f nanoseconds/ %.2f milliseconds/ %.2f seconds.",
				action, datatype, time, time/1000000, (time/1000000)/1000);
	}
}