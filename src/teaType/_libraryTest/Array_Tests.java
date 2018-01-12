package teaType._libraryTest;

import java.util.ArrayList;

import teaType.util.Array;
import teaType.util.rigid.Random;

public class Array_Tests {
	public static void main(String[] args) {
		//arrayMath();
		//arrayJoin();
		arrayConverter();
	}
	
	final static void arrayConverter() {
		int[] iArr = Random.generateInteger(100, 0, true, false, false);
		System.out.println("Integer-Array: ");
		for(int i : iArr) {
			System.out.print(i + " ");
		}
		
		ArrayList<Integer> iList = Array.toArrayList(iArr);
		System.out.println("Integer-ArrayList: ");
		for(int i : iList) {
			System.out.print(i + " ");
		}
	}

	final static void arrayMath() {
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

	final static void arrayJoin() {
		String[] s1 = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j"};
		String[] s2 = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"};
		
		String[] s = Array.fuse(s1, s2);
		
		for(String string : s) {
			System.out.print(string);
		}
	}
}