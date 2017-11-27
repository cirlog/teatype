package teaType._debug.commonTests;

import java.awt.Color;
import java.awt.Graphics;

import javax.swing.JPanel;

public class firstGraphics extends JPanel {
	private static final long serialVersionUID = 1015852072807854606L;
	protected int x;
	protected int y;
	protected int d;
	protected int r;
	protected int w;
	protected int height;
	protected int width;
	protected int r8;
	protected int w3;
	protected int lE;
	protected int rE;
	protected int yE;
	protected int lP;
	protected int yP;
	protected int rP;
	protected double angle;
	protected double bM;
	protected boolean smile;
	protected Color c;

	public firstGraphics(int x, int y, int width, Color c){
		this.x = x;
		this.y = y;
		this.width = width;
		this.height = width;
		this.c = c;
	}

	public void paintComponent(Graphics g){
		super.paintComponent(g);
		g.fillOval(x, y, width, height);
	}
	
	public void orbit() {
		this.x += 5;
		repaint();
	}
}