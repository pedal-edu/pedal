from pedal.sandbox.mocked import MockModule


class MockPlt(MockModule):
    """
    Mock MatPlotLib library that can be used to capture plot data.

    Attributes:
        plots (list of dict): The internal list of plot dictionaries.
    """

    def __init__(self):
        super().__init__()
        self._reset_plots()

    def show(self, **kwargs):
        """ Renders the plot """
        self.plots.append(self.active_plot)
        self._reset_plot()

    def unshown_plots(self):
        """ Checks for plots that are not yet shown. """
        return self.active_plot['data']

    def __repr__(self):
        return repr(self.plots)

    def __str__(self):
        return str(self.plots)

    def _reset_plots(self):
        self.plots = []
        self._reset_plot()

    def _reset_plot(self):
        self.active_plot = {'data': [],
                            'xlabel': None, 'ylabel': None,
                            'title': None, 'legend': False,
                            'kwargs': {},
                            'xlabel_kwargs': {}, 'ylabel_kwargs': {},
                            'title_kwargs': {}, 'suptitle_kwargs': {},
                            'legend_kwargs': {},
                            'other_calls': []}

    def hist(self, data, **kwargs):
        """ Make a histogram """
        label = kwargs.get('label', None)
        self.active_plot['data'].append({'type': 'hist', 'values': data,
                                         'label': label, 'kwargs': kwargs})

    def boxplot(self, data, **kwargs):
        label = kwargs.get('label', None)
        self.active_plot['data'].append({'type': 'boxplot', 'values': data,
                                         'label': label, 'kwargs': kwargs})

    def hlines(self, y, xmin, xmax, **kwargs):
        label = kwargs.get('label')
        self.active_plot['data'].append({'type': 'hlines', 'y': y,
                                         'xmin': xmin, 'xmax': xmax,
                                         'label': label, 'kwargs': kwargs})

    def vlines(self, x, ymin, ymax, **kwargs):
        label = kwargs.get('label')
        self.active_plot['data'].append({'type': 'vlines', 'x': x,
                                         'ymin': ymin, 'ymax': ymax,
                                         'label': label, 'kwargs': kwargs})

    def plot(self, xs, ys=None, **kwargs):
        """ Make a line plot """
        label = kwargs.get('label', None)
        if ys is None:
            self.active_plot['data'].append({'type': 'line',
                                             'x': list(range(len(xs))),
                                             'y': xs, 'label': label,
                                             'kwargs': kwargs})
        else:
            self.active_plot['data'].append({'type': 'line', 'x': xs,
                                             'y': ys, 'label': label,
                                             'kwargs': kwargs})

    def scatter(self, xs, ys, **kwargs):
        """ Make a scatter plot """
        label = kwargs.get('label', None)
        self.active_plot['data'].append({'type': 'scatter', 'x': xs,
                                         'y': ys, 'label': label,
                                         'kwargs': kwargs})

    def bar(self, xs, ys, **kwargs):
        """ Make a bar plot """
        label = kwargs.get('label', None)
        self.active_plot['data'].append({'type': 'bar', 'x': xs,
                                         'y': ys, 'label': label,
                                         'kwargs': kwargs})

    def xlabel(self, label, **kwargs):
        """ Label the x-axis """
        self.active_plot['xlabel'] = label
        self.active_plot['xlabel_kwargs'].update(kwargs)

    def title(self, label, **kwargs):
        """ Make the title """
        self.active_plot['title'] = label
        self.active_plot['title_kwargs'].update(kwargs)

    def suptitle(self, label, **kwargs):
        """ Make the super title """
        self.title(label, **kwargs)
        self.active_plot['suptitle_kwargs'].update(kwargs)

    def ylabel(self, label, **kwargs):
        """ Label the Y-axis """
        self.active_plot['ylabel'] = label
        self.active_plot['ylabel_kwargs'].update(kwargs)

    def legend(self, **kwargs):
        """ Show the legend """
        self.active_plot['legend'] = True
        self.active_plot['legend_kwargs'].update(kwargs)

    def _generate_patches(self):
        def dummy(*args, **kwargs):
            """ This function does nothing. """
            # TODO: Capture name; does this need to be a decorated function?
            self.active_plot['other_calls'].append((args, kwargs))

        return dict(hist=self.hist, plot=self.plot,
                    bar=self.bar, boxplot=self.boxplot,
                    hlines=self.hlines, vlines=self.vlines,
                    scatter=self.scatter, show=self.show,
                    xlabel=self.xlabel, ylabel=self.ylabel,
                    title=self.title, legend=self.legend,
                    xticks=dummy, yticks=dummy,
                    autoscale=dummy, axhline=dummy,
                    axhspan=dummy, axvline=dummy,
                    axvspan=dummy, clf=dummy,
                    cla=dummy, close=dummy,
                    figlegend=dummy, figimage=dummy,
                    suptitle=self.suptitle, text=dummy,
                    tick_params=dummy, ticklabel_format=dummy,
                    tight_layout=dummy, xkcd=dummy,
                    xlim=dummy, ylim=dummy,
                    xscale=dummy, yscale=dummy)
