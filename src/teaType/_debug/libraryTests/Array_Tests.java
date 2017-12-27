package teaType._debug.libraryTests;

import teaType.util.Array;

public class Array_Tests {
	public static void main(String[] args) {
		//arrayMath();
		arrayJoin();
	}
	
	private final static void arrayMath() {
		int[] arr = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
		for(int i : arr) {
			System.out.print(i + " ");
		}
		System.out.println();
		arr = Array.add(arr, 11);
		for(int i : arr) {
			System.out.print(i + " ");
		}
		System.out.println();
		arr = Array.remove(arr, 6);
		for(int i : arr) {
			System.out.print(i + " ");
		}
	}

	private final static void arrayJoin() {
		String[] s1 = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j"};
		String[] s2 = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"};
		
		String[] s = Array.fuse(s1, s2);
		
		for(String string : s) {
			System.out.print(string);
		}
	}
}