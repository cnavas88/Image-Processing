
from skimage.io import imread
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from skimage import color, data, restoration
import numpy as np
from scipy import ndimage
from scipy.misc import imresize


class get_mouse_click():
    """Mouse interaction interface for radial distortion removal.

    """
    def __init__(self, img):
      height, width = img.shape[:2]
      self.figure = plt.imshow(img, extent=(0, width, height, 0))
      plt.gray()
      plt.title('select the object to remove')
      plt.xlabel('Select sets of  points with left mouse button,\n'
                 'click right button to close the polygon.')
      plt.connect('button_press_event', self.button_press)
      plt.connect('motion_notify_event', self.mouse_move)

      self.img = np.atleast_3d(img)
      self.points = []
      self.centre = np.array([(width - 1)/2., (height - 1)/2.])

      self.height = height
      self.width = width

      self.make_cursorline()
      self.figure.axes.set_autoscale_on(False)

      plt.show()
      plt.close()

    def make_cursorline(self):
        self.cursorline, = plt.plot([0],[0],'r:+',
                                    linewidth=2,markersize=15,markeredgecolor='b')

    def button_press(self,event):
        """Register mouse clicks.

        """
        if (event.button == 1 and event.xdata and event.ydata):
            self.points.append((event.xdata,event.ydata))
            print "Coordinate entered: (%f,%f)" % (event.xdata, event.ydata)

            #if len(self.points) % 2 == 0:
            plt.gca().lines.append(self.cursorline)
            self.make_cursorline()

        if (event.button != 1):
            #print "pepito: " ,self.points
            self.points.append((self.points[0][0],self.points[0][1]))
            plt.close()
            return self.points
            #qui
            #print "Removing distortion..."
            #plt.gca().lines = []
            #plt.draw()
            #self.remove_distortion()
            #self.points = []

    def mouse_move(self,event):
        """Handle cursor drawing.

        """
        #pt_sets, pts_last_set = divmod(len(self.points),5)
        #print pts_last_set
        pts_last_set=len(self.points)
        #print pts_last_set2
        pts = np.zeros((pts_last_set+1,2))
        if pts_last_set > 0:
            # Line follows up to 3 clicked points:
            pts[:pts_last_set] = self.points[-pts_last_set:]
            # The last point of the line follows the mouse cursor
        pts[pts_last_set:] = [event.xdata,event.ydata]
        #print pts
        self.cursorline.set_data(pts[:,0], pts[:,1])
        plt.draw()


def compute_mask(width,height,polygon):
    
    img = Image.new('L', (width, height), 0)
    ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
    mask = np.array(img)
    mask100 = 100*np.ones([mask.shape[0],mask.shape[1]])
    mask=mask*101
    mask = 1. - mask; # switch 0s and 1s
    return mask
    
    

#RGB=data.imread('countryside.jpg')
RGB=data.imread('agbar.png')
scale_factor=2
RGB = imresize(RGB, ( RGB.shape[0]/scale_factor,RGB.shape[1]/scale_factor,3),interp='bilinear').astype('float')
img = color.rgb2gray(RGB)
S = img.shape;
S0=S[0]
S1=S[1]
print S0,S1
width=S1;
height=S0;


# GET AREA TO DELETE FROM IMAGE
rdi = get_mouse_click(img)
polygon = rdi.points

# COMPUTE MASK FROM POLYGON
#polygon = [(169.642857,106.565126),(174.369748,470.535714),(344.537815,475.262605),(323.266807,116.018908)]
#polygon = [(333.064516,145.564516),(329.435484,241.129032),(467.338710,258.064516),(473.387097,156.451613)]
#mask=np.ones([S0,S1],dtype=np.double) #if compute_mask is disabled
mask=compute_mask(width,height,polygon)


RGB2 = RGB;
NCTD = 100; # number of columns to delete
