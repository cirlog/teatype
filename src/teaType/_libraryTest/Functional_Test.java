package teaType._libraryTest;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

import com.sun.org.apache.bcel.internal.Constants;

public class Functional_Test {
	public static void main(String[] args) {
		int[] arr = {4, 9, 2, 12, 16, 1, 5};
		
		Integer[] iArr = {1, 2, 3, 4, 5, 6, 7, 8};
		
		//printEvenFP(iArr);
		
		quadraticEvenNumbersJava();
		
		//arr = printEvenFP_alt2(iArr);
		
		//mergeSort(Arrays.asList(34, 3, 21, 6, 0, 32)).forEach(System.out::println);
		
		//System.out.println(factorialFP(3));
		//System.out.println(factorialOOP(3));
		
		//forLoop(5);
		//recursion(0, 5);
	}
	
	public int quadraticAddition(int x, int y) {
		return x*x + y+y;
	}
	
	public void randomizeInput(double d) {
		Random rnd = new Random();
		d = rnd.nextDouble();
	}
	
	static void printEvenOOP(Integer[] array) {
		for(int i = 0; i < array.length; i++) {
			if(array[i] % 2 == 0) {
				System.out.println(array[i]);
			}
		}
	}
	
	static void printEvenOOP_alt1(Integer[] array) {
		for(Integer i : array) {
			if(i % 2 == 0) {
				System.out.println(i);
			}
		}
	}
	
	static void printEvenOOP_alt2(Integer[] array) {
		Integer[] temp = new Integer[array.length];
		for(int i = 0; i < array.length; i++) {
			if(array[i] % 2 == 0) {
				temp[i] = array[i];
				System.out.println(array[i]);
			}
		}
		array = temp;
	}
	
	//Nicht pur funktional, da forEach und System.out.println -> Seiteneffekt
	static void printEvenFP(Integer[] array) {
		Arrays.asList(array).stream().filter(i -> i % 2 == 0).forEach(System.out::println);
	}
	
	static void printEvenFP_alt1(Integer[] array) {
		Arrays.asList(array)
		.stream()
		.filter(i -> i % 2 == 0)
		.forEach(System.out::println);
	}
	
	//Pur funktional
	static int[] printEvenFP_alt2(Integer[] array) {
		return Arrays.asList(array)
		.stream()
		.filter(i -> i % 2 == 0)
		.mapToInt(i -> i)
		.toArray();
	}
	
	static int factorialOOP(int n) {
		int fact = 1;
		for(int i = fact; i <= n; i++) {
			fact *= i;
		}
		return fact;
	}
	
	static int factorialFP(int n) {
		// Wenn n == 0 zutrifft (?) gebe 1 zurück, somit ist Fakultät nur 1, wenn nicht (:), rekursive Methode
		return n == 0 ? 1 : n * factorialFP(n - 1);
	}
	
	static void quadraticEvenNumbersJava() {
		for(int i = 1; i <= 20; i++) {
			if(i % 2 == 0) {
				System.out.println(Math.pow(i, 3));
			}
		}
	}
	
	static void quadraticEvenNumbersHaskell() {
		//mapM_ print [ i^3 | i <- [2, 4 .. 20)] ]
	}
	
	static void forLoop(int max) {
		for(int i = 0; i < max; i++) {
			System.out.println(i);
		}
	}
	
	static void recursion(int i, int max) {
		if(i == max) {
			return;
		}
		System.out.println(i);
		recursion(i+1, max);
	}
	
	/* Functional MergeSort */
	public static List<Integer> merge(List<Integer> list1, List<Integer> list2, List<Integer> accumulator) {
        if (list1.isEmpty()) {
            accumulator.addAll(list2);
        }
        else if (list2.isEmpty()) {
            accumulator.addAll(list1);
        }
        else {
            if (list1.get(0) <= list2.get(0)) {
                accumulator.add(list1.get(0));
                return merge(list1.subList(1, list1.size()), list2, accumulator);
            }
            else {
                accumulator.add(list2.get(0));
                return merge(list1, list2.subList(1, list2.size()), accumulator);
            }
        }
        return accumulator;
    }

    public static List<Integer> mergeSort(List<Integer> list) {
        int mid = list.size()/2;
        if (mid == 0)
            return list;
        return merge(
                mergeSort(list.subList(0, mid)),
                mergeSort(list.subList(mid, list.size())),
                new ArrayList<Integer>());
    }
}

class MergeSort {
	private int[] dataArray, helpArray;
	
	public MergeSort() {}
	
	public void sort (int[] array) {
		this.dataArray = array;
		this.helpArray = new int[array.length - 1];
		mergeSort(0, array.length - 1);
	}
	
	public void mergeSort (int l, int r) {		
		if (l < r) {
			int m = (l + r) / 2;
			mergeSort(l, m);
			mergeSort(m + 1, r);
			merge(l, m, r);
		}
	}

	private void merge (int l, int m, int r) {
	    int index = 0;
	    int otherL = l;
	    
	    while (l <= m) {
	        helpArray[index] = dataArray[l];
	        index++;
	        l++;
	    }
	   
	    index = 0;
	    
	    while (otherL < l && l <= r) {
	    	if (helpArray[index] <= dataArray[l]) {
	            dataArray[otherL] = helpArray[index];
	            index++;
	        } else {
	            dataArray[otherL] = dataArray[l];
	            l++;
	        }
	    	otherL++;
	    }

	    while (otherL < l) {
	        dataArray[otherL] = helpArray[index];
	        otherL++;
	        index++;
	    }
	}
}