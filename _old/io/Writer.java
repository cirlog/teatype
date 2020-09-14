package teaType.util.io;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;

import java.util.ArrayList;

import teaType.data.TeaType;

import teaType.util.StreamBuffer;

public class Writer {
	private FileWriter fw;
	private String path;

	public Writer(String path) {
		this.path = path;
	}
	
	public void teaType(TeaType<String> tt, boolean create, boolean append, boolean linebreak, boolean extraspace) {
		StreamBuffer.fixConsole();
		PrintWriter pw = null;
		try {
			File file = new File(path);
			if(create && !file.exists()) {
				file.createNewFile();
			} else if(create && file.exists()) {
				file.delete();
				file.createNewFile();
			}
			OutputStreamWriter osw = new OutputStreamWriter(new FileOutputStream(file, append), "UTF-8");
			pw = new PrintWriter(new BufferedWriter(osw), true);
			for(int i = 0; i < tt.size(); i++) {
				pw.write(tt.get(i));	
				System.err.print("Writing... ");
				System.out.println(tt.get(i));
				if(linebreak && i < tt.size()-1) {
					pw.write("\n");
				}
			}
			if(extraspace) {
				pw.write("\n");
			}
		} catch(Exception e) {
			e.printStackTrace();
		} finally {
			pw.flush();
			pw.close();
			System.out.print("\nDone! ");
			System.err.print("Process yielded no errors.");
		}
	}

	public void arraylist(ArrayList<String> list, boolean create, boolean append, boolean linebreak, boolean extraspace, boolean verbose) {
		PrintWriter pw = null;
		try {
			File file = new File(path);
			if(create && !file.exists()) {
				file.createNewFile();
			} else if(create && file.exists()) {
				file.delete();
				file.createNewFile();
			}
			OutputStreamWriter osw = new OutputStreamWriter(new FileOutputStream(file, append), "UTF-8");
			pw = new PrintWriter(new BufferedWriter(osw), true);
			for(int i = 0; i < list.size(); i++) {
				pw.write(list.get(i));	
				if(verbose) {
					StreamBuffer.fixConsole();
					System.err.print("Writing... ");
					System.out.println(list.get(i));
				}
				if(linebreak && i < list.size()-1) {
					pw.write("\n");
				}
			}
			if(extraspace) {
				pw.write("\n");
			}
		} catch(Exception e) {
			e.printStackTrace();
		} finally {
			pw.flush();
			pw.close();
			System.out.print("\nDone! ");
			System.err.print("Process yielded no errors.");
		}
	}

	public void string(String content, File file, boolean append) {
		try {
			fw = new FileWriter(file, append);
			fw.write(content);
			fw.close();
		} catch (IOException e) {			
			e.printStackTrace();
		}
	}

	public void array(String[] arr, File file, boolean create, boolean append, boolean whitespace) {
		try {
			if(create) {
				file.delete();
				file.createNewFile();
			}
			fw = new FileWriter(file, append);
			for(int i = 0; i < arr.length; i++) {
				fw.write(arr[i]);
				if(whitespace) {
					fw.write("\n");
				}
			}
			fw.close();
		} catch (IOException e) {			
			e.printStackTrace();
		}
	}
}
