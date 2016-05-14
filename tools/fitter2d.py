from ROOT import gDirectory, TH2F, TF1, TH1D

class Fitter2D(object):

    def __init__(self, *args):
        self.h2d = TH2F(*args)
    
    def draw2D(self, *args):
        self.h2d.Draw(*args)
        self.hmean.Draw('psame')

    def fit(self, bin, opt='0', selection=0): 
        hslice = self.h2d.ProjectionY("{name}{i}".format(i=bin,name=self.h2d.GetName()), bin, bin, "")
        setattr(self, '{name}hslice{i}'.format(i=bin,name=self.h2d.GetName()), hslice)
        if not hslice.GetEntries(): 
            return 0., 0., 0., 0., 0., 0., 0.
        mean = hslice.GetMean()
        sigma = hslice.GetRMS()
        func = TF1('fitgauss','gaus')
        if selection:
            func.SetRange(mean-(selection*sigma), mean+(selection*sigma))
            func.SetParLimits(2, 0, selection*sigma)
        func.SetParameter(1, mean)
        func.SetParameter(2, sigma)
        hslice.Fit('fitgauss', opt)
        #func = hslice.GetFunction('gauss')
        x = self.h2d.GetXaxis().GetBinCenter(bin)
        dx = self.h2d.GetXaxis().GetBinWidth(bin)
        mean = func.GetParameter(1)
        dmean = func.GetParError(1)
        sigma = func.GetParameter(2)
        dsigma = func.GetParError(2)
        ndf = func.GetNDF()
        if ndf:
            chi2ndf = func.GetChisquare()/ndf
        else:
            chi2ndf = 0.
        return x, dx, mean, dmean, sigma, dsigma, chi2ndf

    def fit_slices(self, selection=0):
        nbin = self.h2d.GetNbinsX()
        ymin = self.h2d.GetXaxis().GetXmin()
        ymax = self.h2d.GetXaxis().GetXmax()
        self.hmean = TH1D('hmean','Fitted value of mean', 
                              nbin, ymin, ymax)
        self.hsigma = TH1D('hsigma','Fitted value of Sigma',
                               nbin, ymin, ymax)
        #self.hchi2ndf = TH1D('hchi2ndf','Fit Chi2/ndf',
        #                       nbin, ymin, ymax)
        for bin in range(nbin):
            x, dx, mean, dmean, sigma, dsigma, chi2ndf = self.fit(bin, opt='0 B', selection=selection)
            if chi2ndf>3:
                continue
            self.hmean.SetBinContent(bin, mean)
            self.hmean.SetBinError(bin, dmean)
            self.hsigma.SetBinContent(bin, sigma)
            self.hsigma.SetBinError(bin, dsigma)
            #self.hchi2ndf.SetBinContent(bin, chi2ndf)


        #self.h2d.FitSlicesY()
        #self.hmean = gDirectory.Get( self.h2d.GetName() + '_1' )
        #self.hsigma = gDirectory.Get( self.h2d.GetName() + '_2' )
        # self.hsigma.SetYTitle('#sigma(MET_{x,y})')
        #self.hchi2 = gDirectory.Get( self.h2d.GetName() + '_chi2' )

    def format(self, style, xtitle):
        for hist in [self.hmean, self.hsigma, self.hchi2]: 
            style.format(hist)
            hist.SetTitle('')
            hist.SetXTitle(xtitle)
            
