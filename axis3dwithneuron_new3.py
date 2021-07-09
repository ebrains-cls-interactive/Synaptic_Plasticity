from matplotlib.pyplot import cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from neuron import h
from neuron.gui2.utilities import _segment_3d_pts

class Axis3DWithNEURON(Axes3D):
    def auto_aspect(self):
        """sets the x, y, and z range symmetric around the center

        Probably needs a square figure to preserve lengths as you rotate."""
        bounds = [self.get_xlim(), self.get_ylim(), self.get_zlim()]
        half_delta_max = max([(item[1] - item[0]) / 2 for item in bounds])
        xmid = sum(bounds[0]) / 2
        ymid = sum(bounds[1]) / 2
        zmid = sum(bounds[2]) / 2
        #self.auto_scale_xyz([xmid - half_delta_max, xmid + half_delta_max],
        #                    [ymid - half_delta_max, ymid + half_delta_max],
        #                    [zmid - half_delta_max, zmid + half_delta_max])
        self.auto_scale_xyz([xmid - 160, xmid + 160],
                            [ymid - 160, ymid + 160],
                            [zmid - 160, zmid + 160])

    def mark(self, segment, marker='or', number=1, **kwargs):
        """plot a marker on a segment
        
        Args:
            segment = the segment to mark
            marker = matplotlib marker
            **kwargs = passed to matplotlib's plot
        """
        # TODO: there has to be a better way to do this
        sec = segment.sec
        n3d = sec.n3d()
        arc3d = [sec.arc3d(i) for i in range(n3d)]
        x3d = np.array([sec.x3d(i) for i in range(n3d)])
        y3d = np.array([sec.y3d(i) for i in range(n3d)])
        z3d = np.array([sec.z3d(i) for i in range(n3d)])
        seg_l = sec.L * segment.x
        x = np.interp(seg_l, arc3d, x3d)
        y = np.interp(seg_l, arc3d, y3d)
        z = np.interp(seg_l, arc3d, z3d)
        self.plot([x], [y], [z], marker)
        self.text(x, y, z, str(number), color='red', weight='bold')



    def shapeplot(self,
                sections=None,
                variable=None,
                cmap=cm.cool,
                **kwargs):
        """
        Plots a 3D shapeplot
        Args:
            sections = list of h.Section() objects to be plotted
            **kwargs passes on to matplotlib (e.g. linewidth=2 for thick lines)
        Returns:
            lines = list of line objects making up shapeplot
        
        Adapted from
        https://github.com/ahwillia/PyNeuron-Toolbox/blob/master/PyNeuronToolbox/morphology.py
        Accessed 2019-04-11, which had an MIT license
        """
        
        # Default is to plot all sections. 
        if sections is None:
            sections = list(h.allsec())

        h.define_shape()

        # default color is black
        kwargs.setdefault('color', 'black')

        # Plot each segement as a line
        lines = []
        vals = []
        diams=[]
        for sec in sections:
            all_seg_pts = _segment_3d_pts(sec)
            for seg, (xs, ys, zs, _, _) in zip(sec, all_seg_pts):
                line, = self.plot(xs, ys, zs, '-', **kwargs)
                if variable is not None:
                    try:
                        if '.' in variable:
                            mech, var = variable.split('.')
                            val = getattr(getattr(seg, mech), var)
                        else:
                            val = getattr(seg, variable)
                    except AttributeError:
                        # leave default color if no variable found
                        val = None
                    vals.append(val)
                diams.append(seg.diam)
                lines.append(line)
        
        if variable is not None:
            have_values = True
            try:
                val_min = min(val for val in vals if val is not None)
                val_max = max(val for val in vals if val is not None)
                val_range = val_max - val_min
            except ValueError:
                have_values = False
            if have_values and val_range:
                for sec in sections:
                    for line, val, diam in zip(lines, vals, diams):
                        if val is not None:
                            #col = cmap(int(255 * (val - val_min) / (val_range)))
                            line.set_color('k')
                            line.set_linewidth(diam)
        return lines

#if __name__ == '__main__':
#    cell = Cell(0)
#    h.finitialize(-65)
#    h.distance(0, cell.soma[0](0.5))
#    for sec in cell.all:
#        for seg in sec:
#            seg.v = h.distance(seg)

#    fig = plt.figure()
#    ax = Axis3DWithNEURON(fig)
#    ax.grid(False)
#    ax.axis('off')
#    ax.shapeplot(color='red', variable='v')
#    ax.mark(cell.soma[0](0.5))
#    ax.mark(cell.axon[53](1))
#    ax.mark(cell.apic[33](0.1), marker='ob')
#    plt.show()
