cs_long_name = 'Linear Regression'
mode='analysis'

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as _p
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk, FigureCanvasAgg

from io import BytesIO
import base64 as _b64

class PlotWindowBase(_p.Figure):
    """
    Tk window containing a matplotlib plot.  In addition to the functions
    described below, also supports all functions contained in matplotlib's
    Axes_ and Figure_ objects.

    .. _Axes: http://matplotlib.sourceforge.net/api/axes_api.html
    .. _Figure: http://matplotlib.sourceforge.net/api/figure_api.html
    """
    def __init__(self, title="Plotting Window", visible=True):
        """
        :param title: The title to be used for the window initially
        :param visible: Whether to actually display a Tk window (set to
                        ``False`` to create and save plots without a window
                        popping up)
        """
        _p.Figure.__init__(self)
        self.ax = self.add_subplot(111)
        self.visible = visible
        if self.visible:
            self.canvas = FigureCanvasTkAgg(self, tkinter.Tk())
            self.title(title)
            self.makeWindow()
            self.show()
        else:
            self.canvas = FigureCanvasAgg(self)

    def makeWindow(self):
        """
        Pack the plot and matplotlib toolbar into the containing Tk window
        (called by initializer; you will probably never need to use this).
        """
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        self.toolbar = NavigationToolbar2Tk( self.canvas, self.canvas._master )
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    def destroy(self):
        """
        Destroy the Tk window.  Note that after calling this method (or
        manually closing the Tk window), this :py:class:`PlotWindow` cannot be
        used.
        """
        try:
            self.canvas._master.destroy()
        except:
            pass # probably already destroyed...

    def clear(self):
        """
        Clear the plot, keeping the Tk window active
        """
        self.clf()
        self.add_subplot(111)
        if self.visible:
            self.show()

    def show(self):
        """
        Update the canvas image (automatically called for most functions)
        """
        self.canvas.draw()

    def __getattr__(self, name):
        show = True
        if name.startswith('_'):
            name = name[1:]
            show = False
        if hasattr(self.axes[0], name):
            attr = getattr(self.axes[0], name)
            if hasattr(attr,'__call__'):
                if show:
                    def tmp(*args,**kwargs):
                        out = attr(*args,**kwargs)
                        if self.visible:
                            self.show()
                        return out
                    return tmp
                else:
                    return attr
            else:
                return attr
        else:
            raise AttributeError("PlotWindow object has no attribute %s" % name)

    def title(self,title):
        """
        Change the title of the Tk window
        """
        self.ax.set_title(title)

    def legend(self, *args):
        """
        Create a legend for the figure (requires plots to have been made with
        labels)
        """
        handles, labels = self.axes[0].get_legend_handles_labels()
        self.axes[0].legend(handles, labels)
        if self.visible:
            self.show()

    def save(self, fname):
        """
        Save this plot as an image.  File type determined by extension of filename passed in.
        See documentation for savefig_.

        :param fname: The name of the file to create.

        .. _savefig: http://matplotlib.sourceforge.net/api/figure_api.html
        """
        self.savefig(fname)

    def stay(self):
        """
        Start the Tkinter window's main loop (e.g., to keep the plot open at
        the end of the execution of a script)
        """
        self.canvas._master.mainloop()


def PlotWindow(title="Plotting Window"):
    class _PlotWindow(PlotWindowBase):
        def __init__(self, title="Plotting Window"):
            PlotWindowBase.__init__(self, title, visible=False)

        def _show(self, width="75%"):
            sio = BytesIO()
            self.savefig(sio, format='png', facecolor='none')
            return '<img src="data:image/png;base64,%s" width="%s"/>' % (_b64.b64encode(sio.getvalue()).decode(), width)
    return _PlotWindow(title)


ys = [-26.85901649618508, -4.82309989277328, 358.12325659886665, -236.27303224345013, 78.96311735375048, -122.0718747926675, -91.794917932851, 156.92288603409375, 77.76372162876706, 134.08018802466293, 421.2164012311623, -102.44084767789477, 69.05193026508634, -65.1707634424306, -6.811873517536455, 14.464555720475445, 123.35092804160584, 269.2411300965563, 283.6126314082743, 249.5593597768601, -45.93699758535121, 160.9929838505804, -11.486651027732734, 34.89429129194224, 227.0114874496006, 453.94991714737176, 159.59340132582852, 305.53172734934645, 209.30183669664237, 377.794764790121, 316.6853125571703, 242.97813270158048, 99.55136064457564, 380.8281222370041, 517.9678491133832, 152.82974416562115, 501.3107247844115, 385.00869117981006, 260.76894288405657, 245.62085551544348, 381.93212971867905, 282.37383569434684, 255.6684633511091, 528.9665009201663, 214.89786230001818, 198.47447067627894, 583.0632870160896, 556.0811185746013, 334.2809525610168, 743.3044708948721, 279.7165711058779, 755.3224521456882, 200.5387369220224, 138.47687852393108, 197.63575541409483, 181.71767331525095, 376.89074479245284, 652.3613138217629, 381.4275586382469, 476.0995327254289, 461.46417474466193, 423.8593541888392, 503.3792036069044, 567.7438934709394, 296.9627154414269, 183.36747560528335, 714.4663522847009, 620.296512084993, 315.16553989225656, 644.953867681399, 381.11694172321086, 392.7101550383068, 474.0136908544534, 556.91031778183, 625.6146302263054, 561.5239749404492, 491.3389262641957, 396.09862792366937, 328.9611909946891, 442.51020674282574, 637.3002734137215, 820.1180066579375, 704.0222105099904, 749.7416740127572, 571.3375044210943, 740.3732575510189, 508.23757383850227, 805.9057544835931, 652.1781007402574, 331.2078936574819, 659.394649695742, 779.5249873375656, 417.1728951942524, 727.5381994766699, 846.8237700909708, 372.6078315611338, 735.4394177096567, 359.3157568184622, 742.5223675039202, 645.445434892132]
xs = [103+i for i in range(len(ys))]
