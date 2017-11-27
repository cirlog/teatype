package teaType._debug.commonTests;

import java.io.File;
import java.io.FileNotFoundException;

import java.util.ArrayList;
import java.util.Scanner;

public class Reader {

	protected File selectedFile;
	protected ArrayList<String> list;
	protected File fileCache;
	protected ArrayList<String> listCache;

	public Reader () {
	}

	public String[] readFile(File selectedFile) throws FileNotFoundException {
		fileCache = this.selectedFile;
		this.selectedFile = selectedFile;
		String[] superString = null;
		Scanner input = new Scanner (selectedFile);
		Scanner listToArray = new Scanner (selectedFile);
		ArrayList<String> list = new ArrayList<String>();
		
		while (input.hasNext()) {
			list.add(input.nextLine());
		}
		listCache = this.list;
		this.list = list;

		superString = new String[list.size()];
		
		int i = 0;
		while (listToArray.hasNext()) {
			superString[i] = listToArray.next();
			i++;
		}
		input.close();
		listToArray.close();
		return superString;
	}

	public int getLength() throws FileNotFoundException {
		int i = (readFile(selectedFile).length);
		return i;
	}
	
	public ArrayList<String> getList() {
		return list;
	}
	
	public File getFile() {
		return selectedFile;
	}
	
	public void emptyCache() {
		listCache = null;
		fileCache = null;
	}
}
