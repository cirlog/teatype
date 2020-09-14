package teaType.util.io;

import java.io.File;
import java.io.FileNotFoundException;

import java.util.ArrayList;
import java.util.Scanner;

public class Reader {
	// TODO: Generalisierung & Auslagerung der Konvertierung in eigene Klassen & PrintStream statt Filewriter
	protected String path, fileCache;
	private String[] sArr;
	private int count;
	//private int[] iArr;
	protected ArrayList<String> list, listCache;
	private Scanner in;

	public Reader() {
		count = 0;
	}

	public int[] integerArray(String selectedFile) {
		try{
			File file = new File(selectedFile);
			Scanner input = new Scanner (file);
			ArrayList<String> list = new ArrayList<String>();

			while(input.hasNextInt()) {
				String temp = input.next();
				if(temp.equals("")){
					continue;
				}
				list.add(temp);
				count++;
			}
			String[] superString = new String[list.size()];

			int temp;
			int[] array = new int[count];

			for(int i = 0; i < list.size(); i++){
				superString[i] = list.get(i);
				temp = Integer.parseInt(superString[i]);
				array[i] = temp;
			}

			input.close();
			return array;
		} catch (FileNotFoundException exc) {
			System.out.println("File cannot be found");
		}
		return null;	
	}

	public String[] stringArray(String path) {
		try{
			File file = new File(path);
			in = new Scanner(file);
			list = new ArrayList<String>();
			while(in.hasNext()) {
				String temp = in.nextLine();
				if(temp.equals("")){
					continue;
				}
				list.add(temp);
			}
			sArr = new String[list.size()];
			for(int i = 0; i < list.size(); i++){
				sArr[i] = list.get(i);
			}
			in.close();
			return sArr;
		} catch (FileNotFoundException exc) {
			System.out.println("Error 404: File not found.");
		}
		return null;
	}

	/*
	public String[] readFile(String selectedFile, boolean useDelimiter, Pattern delimiter) {
		try{
			File file = new File(selectedFile);
			Scanner in = new Scanner(file);
			ArrayList<String> list = new ArrayList<String>();
			if(useDelimiter) {
				in.useDelimiter(delimiter);
				ArrayList<String> temp = new ArrayList<String>();
				while(in.hasNextLine()) {
					temp.add(in.nextLine());
				}
				list = temp;
			} else {
				while (in.hasNext()) {
					String temp = in.nextLine();
					if(temp.equals("")){
						continue;
					}
					list.add(temp);
				}
			}

			String[] superString = new String[list.size()];

			for(int i = 0; i < list.size(); i++){
				superString[i] = list.get(i);
			}

			in.close();
			return superString;
		} catch (FileNotFoundException exc) {
			System.out.println("File cannot be found");
		}
		return null;
	}

	public static int[] fileToIntegerArray(String dat) {
		int [] A = null;
		FileInputStream fis = null;
		try {
			fis = new FileInputStream(dat);
		}
		catch ( Exception e) {
			System.out.println("'dat' konnte nicht geoeffnet werden");

		}
		try {
			InputStreamReader isr   = new InputStreamReader(fis);
			BufferedReader    br = new BufferedReader   (isr);

			String einZeile;
			einZeile = br.readLine();
			int anz = new Integer(einZeile);

			A = new int[anz];
			for (int i = 0; i < anz; i++){
				einZeile = br.readLine();

				if (einZeile == null) break;     // Ende der Datei erreicht
				//		         System.out.print(einZeile);
				int j = new Integer(einZeile);
				A[i] = j;
			}
		}
		catch (Exception e) {
			System.out.println("Einlesen nicht erfolgreich");
		}
		return A;
	}
	 */
	
	public void emptyCache() {
		listCache = null;
		fileCache = null;
	}

	public int getLength() { return list.size(); }

	public ArrayList<String> getList() { return list; }

	public String getFile() { return path; }
}