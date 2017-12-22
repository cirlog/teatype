package teaType._debug.commonTests;

import java.io.PrintWriter;

public class TemporaryTestEnvironment {
	public static void main(String[] args) {
		PrintWriter out = new PrintWriter(System.out, true);
		
		threadDivision(out);
	}
	
	final static void threadDivision (PrintWriter out) {
		int numberThreads = 1;
		int sampleRate = 8;
		int sum = sampleRate / numberThreads;
		if(sum < 1) {
			sum = 1;
		}
		out.println(sum);
	}
}