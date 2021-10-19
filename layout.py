'''
Created on 22 Oct 2018
Updated 29 Jan 2021

@author: thomasgumbricht
'''

# Package application imports

#from layout import mj_legends as mj_legends

import os

import array as arr



import png as img_png

import svgwrite

import subprocess

from geoimagine.params import RasterPalette

class ProcessLayout():
    '''
    '''
    
    def __init__(self, pp, session):
        '''
        '''
        
        self.session = session
                
        self.pp = pp  
        
        self.verbose = self.pp.process.verbose   
        
        self.session._SetVerbosity(self.verbose)     
        
        # Direct to subprocess
 
        if self.verbose > 1:
            
            print ('    Starting ProcessLayout: ',self.pp.process.processid )
            
        if self.pp.process.processid == 'AddRasterPalette':
            
            self._AddRasterPalette()
            
        elif self.pp.process.processid == 'CreateLegend':
            
            self._CreateRasterLegend()
            
        elif self.pp.process.processid == 'CreateScaling':
            
            self._AddRasterScaling()
            
        elif self.pp.process.processid == 'ExportLegend':
            
            self._ExportRasterLegend()
        
        elif self.pp.process.processid == 'AddMovieClock':
            
            self._MovieClock()
            
        elif self.pp.process.processid in ['ExportTilesToByte','ExportShadedTilesToByte']:
            
            # Only initiate
            pass
            
        else:
            
            exitstr = 'ProcessLayout process %s not available' %(self.pp.process.processid)
            
            exit(exitstr)
            
    def _AddRasterPalette(self):
        '''
        '''
        
        # Convert the parameters to a dict [palette, compid, access, default, setcolor]
        queryD = dict( list( self.pp.process.parameters.__dict__.items() ) )
        
        # pop the setcolor key
        queryD.pop('setcolor')
        
        defaultPalette = queryD.pop('default')
        
        # Set the user as the owner
        queryD['owner'] = self.pp.userproject.userid
        
        colorD = {}
        
        # Loop over all setcolor entries
        paletteD =  dict( list( self.pp.process.parameters.setcolor.__dict__.items() ) )
        
        for key in paletteD:
            
            try:
            
                colorD[key] = dict (list (paletteD[key].__dict__.items() ) )
                
            except:
                                        
                exitstr = 'ERROR in setting color', key, self.pp.process.parameters.palette
                
                                
                exit(exitstr)
                                        
        self.session._ManageRasterPalette(queryD, colorD,
                    self.pp.process.overwrite,self.pp.process.delete)
             
    def _CreateRasterLegend(self):
        '''
        '''
        
        # Convert the parameters to a dict 
        queryD = dict( list( self.pp.process.parameters.__dict__.items() ) )
        
        #for comp in self.pp.process.comp:
        for comp in self.pp.srcCompD:
            
            compD = dict( list( self.pp.srcCompD[comp].__dict__.items() ) )
            
            self.session._ManageRasterLegend(queryD, compD,
                        self.pp.process.overwrite ,self.pp.process.delete)
        
    def _AddRasterScaling(self):
        '''
        '''

        # Convert the parameters to a dict:  
        paramsD =  dict( list( self.pp.process.parameters.__dict__.items() ) )
        
        # CLoop over the compositions
        for comp in self.pp.process.comp:
            
            # Convert each composition to a dict
            d =  dict( list( comp.__dict__.items() ) )
            
            for k in d:
                
                compD = dict( list( d[k].__dict__.items() ) )
        
            # Add to database
            self.session._ManageRasterScaling(paramsD,
                        compD,self.pp.process.overwrite,self.pp.process.delete)
            
    def _AddMovieClock(self):
        '''
        '''
        
        # Convert the parameters to a dict:  
        paramsD =  dict( list( self.pp.process.parameters.__dict__.items() ) )
        
        self.session._ManageMovieClock(paramsD,
                self.pp.process.overwrite, self.pp.process.delete)
    
    
    def _SelectCompFormat(self):
        #Get the data measure from the compid
        '''
        print (self.process.proj.system)
        FISK
        query = {'system':self.process.proj.system,'compid':self.compid}
        rec = self.session._GetCompFormat(query)
        self.measure = rec[3]
        '''
        self.measure = 'R'
        
    def _SelectScaling(self,comp):
        '''
        '''
        # This is identical to the same function in
        
        scalingD = self.session.IniSelectScaling(self.pp.srcCompD[comp])
        
        self.scaling = lambda: None 
        
        for key, value in scalingD.items():
        
            setattr(self.scaling, key, value)
            
            
    def _SelectLegend(self,comp):
        '''THIS IS A DUPLICATE FROM export
        Select legend from database
        '''
        
        legendD = self.session.IniSelectLegendStruct(self.pp.srcCompD[comp])
        
        self.legend = lambda: None
        
        for key, value in legendD.items():
            
            setattr(self.legend, key, value)
            
        self.legend.frame = int(self.legend.framestrokewidth+0.99)
        
    def _ExportRasterLegend(self):
        '''
        '''
        
        self.imgD = {}
        
        #Export each composition (if several)
        # Convert the parameters to a dict 
        #queryD = dict( list( self.pp.process.parameters.__dict__.items() ) )
        
        for comp in self.pp.srcCompD:
            
            compD = dict( list( self.pp.srcCompD[comp].__dict__.items() ) )
            
            self.compid = compD['compid']
                        
            #Create the target paths
            self.pngFP = os.path.join('/Volumes',self.pp.process.dstpath.volume,'legends','png')
            
            self.pdfFP = os.path.join('/Volumes',self.pp.process.dstpath.volume,'legends','pdf')
            
            self.svgFP = os.path.join('/Volumes',self.pp.process.dstpath.volume,'legends','svg')
            
            if not os.path.exists(self.pngFP):
                
                os.makedirs(self.pngFP)
                
            if not os.path.exists(self.pdfFP):
                
                os.makedirs(self.pdfFP)
                
            if not os.path.exists(self.svgFP):
                
                os.makedirs(self.svgFP)
                
            # Set the filenames  
            self.svgFN = '%s_%s.svg' %(self.compid, self.pp.process.parameters.palette)
            
            self.svgFPN = os.path.join(self.svgFP,self.svgFN)
            
            self.pngFPN = self.svgFPN.replace('.svg','.png')
            
            self.jpgFPN = self.svgFPN.replace('.svg','.jpg')
            
            if not self.pp.process.overwrite:
            
                if os.path.exists(self.svgFPN) and os.path.exists(self.pngFPN):
                    
                    if not self.pp.process.parameters.jpg or os.path.exists(self.jpgFPN):
                        
                        return
                
            #Get the measure (i.e. O,R,I)
            self._SelectCompFormat()
            
            #Get the scaling
            self._SelectScaling(comp)
            
            #Get the legend
            self._SelectLegend(comp)
            
            #Get the palette
            self._SelectPaletteColors()
            
            #Set the dimensions
            self._SetLegendDim()

            if self.measure == 'N' or self.pp.process.parameters.legendnominal: 
                
                self._CreateFramesN() 
                        
            else:
                self._CreateFramesOIR()
                
            self._WriteLegendImgs()
                                         
            self._ConstructSVG()
            
    def _SelectPaletteColors(self):
        '''Select the palette colors from the database
        '''
        if self.pp.process.parameters.palette == 'default':
            #Look for a default palette for this composition
            query = {'compid':self.compid}
            self.palettename = self.session._SelectCompDefaultPalette(query)
            if self.palettename == None:
                exitstr = 'No default palette for compid %(c)s' %{'c':self.compid}
                exit(exitstr)
        else:
            self.palettename = self.pp.process.parameters.palette
        #Create the palette valriable
        self.palette = lambda: None
        self.svgPalette = {}
        self.svgColor = {}
        
        #Get the palette
        query = {'palette':self.palettename}
        paramL = ['value','red','green','blue','alpha','label','hint']
        recs = self.session._SelectPaletteColors(query,paramL)
        
        recs.sort() 
        recs.reverse() 
        maxDone = False
        for rec in recs:
            if 0 <= rec[0] <= 250:
                #self.svgPalette[rec[0]] = [rec[1],rec[2],rec[3]]
                self.svgPalette[rec[0]] = 'rgb(%(r)d,%(g)d,%(b)d)' %{ 'r':rec[1], 'g':rec[2], 'b':rec[3] }
                if not maxDone:
                    maxLeg = rec[0]
                    maxDone = True
                minLeg = rec[0]
            else:
                self.svgColor[rec[0]] = 'rgb(%(r)d,%(g)d,%(b)d)' %{ 'r':rec[1], 'g':rec[2], 'b':rec[3] }
        recs.sort()
        self.palette.items = recs
        self.palette.paletteL = []
        

        palette = RasterPalette()
        palette.SetTuplePalette(recs, self.palettename)
        
        
        
        for i in range(256):             
            self.palette.paletteL.append(palette.colortable.GetColorEntry(i))
            
        self.palette.legIdL = []
        self.palette.stickIdL =[]
        self.palette.coreIdL = [] 
        
        for rec in recs:
            self.palette.legIdL.append(rec[0])
            if rec[0] <= 250:
                self.palette.coreIdL.append(rec[0])
                if rec[6] != 'NA':
                    self.palette.stickIdL.append(rec[0])              
        #self.palette.minLeg = max(recs[0][0],self.legend.palmin)
        #self.palette.maxLeg = min(recs[len(recs)-1][0],self.legend.palmax) 
        self.palette.minLeg = max(minLeg, self.legend.palmin)
        self.palette.maxLeg = min(maxLeg,self.legend.palmax) 
        #self.palette.maxLeg = min(max(self.palette.coreIdL),self.legend.palmax,250)
        
    def _SetLegendDim(self):
        '''
        '''
        
        self.legend.cols = self.legend.width
        self.legend.lins = self.legend.height   
        self.sideFrame = arr.array('B',(254 for i in range(self.legend.frame) ) )
        self.topBotFrame = arr.array('B',(254 for i in range(self.legend.cols*self.legend.frame) ) )
        self.frameStick =  arr.array('B',(254 for i in range(self.legend.sticklen) ) )    
    
    
    def _CreateFramesN(self):
        '''Separate frames for nominal data
        '''
        self.legend.totHeight = 0
        self._SeparatePngFrames() 
        for i in range(self.palette.minLeg,self.palette.maxLeg+1):
            if i in self.palette.legIdL:
                #self.CreateSepFrame(self.legend.totHeight,cols,pngFP,i)
                self._CreateSepFrame(i)
                
                
    def _SeparatePngFrames(self): 
        ''' CREATE THE SEPARATE FRAMES'''    
        for j in range(1,6):
            item = 'two5%s' %(j)
            nr = '25%s' %(j)
            i = int(nr)
            if getattr(self.legend, item):
                self.CreateSepFrame(i)  
                
    def _CreateSepFrame(self,i):
        '''
        '''
        INDEX = [] 
        print (self.legend.separatebuffer)
        print (self.legend.frame)
        sepLins = self.legend.separatebuffer + len(self.legend.frame)*2
        self.legend.totHeight += sepLins + self.legend.buffer 
        INDEX.extend(self.topBotFrame)
        for k in range(self.legend.separatebuffer):  
            INDEX.extend(self.sideFrame)
            for l in range(self.legend.cols-self.legend.frame*2):
                INDEX.append(i) 
            INDEX.extend(self.sideFrame)
        INDEX.extend(self.topBotFrame)
        imgFN = '%s_%s-%s.png' %(self.compid,self.paletteName,i)
        imgFPN = os.path.join(self.pngFP,imgFN)
        self.imgD[i] = {'fpn':imgFPN,'lins':sepLins,'cols':self.legend.cols,'arr':INDEX,'typ':'singlefill'}
                
    def _CreateFramesOIR(self):
        '''
        '''

        INDEX = []
        linsperitem = int(self.legend.lins/(self.palette.maxLeg-self.palette.minLeg))
        printStretch = linsperitem*(self.palette.maxLeg-self.palette.minLeg+1)
        totLins = linsperitem*(self.palette.maxLeg-self.palette.minLeg+1)+(self.legend.frame*2)
        self.legend.totHeight = linsperitem*(self.palette.maxLeg-self.palette.minLeg+1)+(self.legend.frame*2)      
        self._SeparatePngFrames()
        if float(self.legend.height-self.legend.totHeight) / (self.palette.maxLeg-self.palette.minLeg) > 0.5:
            linsperitem += 1
            totLins += (self.palette.maxLeg-self.palette.minLeg+1)
            printStretch += (self.palette.maxLeg-self.palette.minLeg+1)
        for i in range(self.palette.minLeg,self.palette.maxLeg+1):
            for k in range(linsperitem):
                INDEX.extend(self.sideFrame)
                if i in self.palette.stickIdL:
                    INDEX.extend(self.frameStick)        
                    for l in range(self.legend.cols-len(self.sideFrame)*2-len(self.frameStick)):
                        INDEX.append(i)   
                else:
                    for l in range(self.legend.cols-self.legend.frame*2):
                        INDEX.append(i) 
                INDEX.extend(self.sideFrame)          
        # Put the top frame
        INDEX.extend(self.topBotFrame)
        INDEX.reverse()  
        # Put the bottom frame
        INDEX.extend(self.topBotFrame)
        imgFN = '%s_%s.png' %(self.compid,self.palettename)
        imgFPN = os.path.join(self.pngFP,imgFN)
        self.imgD[0] = {'fpn':imgFPN,'lins':totLins,'cols':self.legend.cols,'arr':INDEX,'typ':'gradientfill'}
                  
    def _WriteLegendImgs(self):
        '''
        '''
        for item in self.imgD:    
            if not len(self.imgD[item]['arr']) == self.legend.cols * self.imgD[item]['lins']:
                print ( len(self.imgD[item]['arr']) ) 
                print ( self.legend.cols * self.imgD[item]['lins'] )
                exit('Error in legend dimensions')
            self._WritePng(self.imgD[item]['arr'],self.imgD[item]['fpn'],self.legend.cols,self.imgD[item]['lins'],self.palette.paletteL)

    def _WritePng(self, INDEX,imageFPN,cols,lins,paletteL):
        '''
        '''
        
        RGB = arr.array('B',(int(i) for i in INDEX))
        f = open(imageFPN, 'wb')      # binary mode   
        w = img_png.Writer(width=cols, height=lins, greyscale=False, bitdepth=8, palette=paletteL, chunk_limit = cols)
        w.write_array(f, RGB)
        f.close()
        
    def _ConstructSVG(self):
        '''
        '''    
        #set the origin for the printing
        #The yPos should be conditions given the labels in the legend

        self.xPos,self.yPos = self.legend.margin[3],self.legend.margin[2]+self.legend.fontsize/1.75 + self.legend.framestrokewidth
        self._SetTwoFivePrintPos()

        if self.measure == 'N' and self.legend.matrix:
            self._SetValuePrintPosNM()
        else:
            self._SetValuePrintPos()
            if self.measure != 'N': 
                self._SetValuePrintPosR()

        #Add vertical space for title 
        self.yPos += self.legend.textpadding[0]

        self._SetDrawText()
        
        #Add top margin
        self.yPos += self.legend.margin[0]
        
        # With the dimensions set to 300 pixels in y, the font-size factor becomes 1.33
        self.scalefac = self.legend.pngheight/self.yPos
        self.fontfac = 1.33

        self.width = self.legend.pngwidth
        self.height = self.legend.pngheight
        
        xsize = '%(x)dpx' %{'x':self.width}
        ysize = '%(x)dpx' %{'x':self.height}
        self.dwg = svgwrite.Drawing(self.svgFPN, size=(xsize, ysize), profile='full', debug=True)
        # set user coordinate space
        self.dwg.viewbox(width=self.width, height=self.height)

        #draw the images
        self._CanvasDrawImages()
        
        #draw the text
        self._CanvasDrawText()
        
        #save 
        self.dwg.save()
        
        #convert to png
        self._DwgToPng(self.svgFPN,self.pngFPN,self.jpgFPN)
        
    def _SetTwoFivePrintPos(self):   
        #get the print positions for items 255 downto 251:
        for i in range(255,250,-1):
            if i in self.imgD:
                self.imgD[i]['ymin'] = self.yPos
                self.yPos += self.imgD[i]['lins']
                self.imgD[i]['ymax'] = self.yPos
                self.yPos += self.legend.buffer
                self.imgD[i]['ycenter'] = int((self.imgD[i]['ymax']+self.imgD[i]['ymin'])/2)
                self.imgD[i]['xmin'] = self.xPos
                self.imgD[i]['xmax'] = self.legend.cols+self.imgD[i]['xmin'] 
                self.imgD[i]['xcenter'] = int((self.imgD[i]['xmax']+self.imgD[i]['xmin'])/2)
                
    def _SetValuePrintPosNM(self):
        #Start from the top
        for i in range(0,251):
            if i in self.imgD: 
                topy = self.yPos+(len(self.palette.coreIdL)/self.legend.columns)*(self.imgD[i]['lins']+self.legend.buffer)
                posL = [j for j in range(len(self.palette.coreIdL))]
                item = self.palette.coreIdL.index(i)
                for c in range(self.legend.columns):
                    testL = [j for j in posL if int(j-c) % self.legend.columns == 0]
                    if item in testL:
                        break
                itemx = c
                itemy = testL.index(item)
                #get top y
                self.imgD[i]['ymax'] = topy-itemy*(self.imgD[i]['lins']+self.legend.buffer)
                #get bottom y
                self.imgD[i]['ymin'] = self.imgD[i]['ymax']-self.imgD[i]['lins']
                #150 is a fixed offset to make place for text
                self.imgD[i]['xmin'] = self.xPos+150+itemx*(self.legend.cols+self.legend.buffer)
                self.imgD[i]['xmax'] = self.legend.cols+self.imgD[i]['xmin']          
                self.imgD[i]['ycenter'] = int((self.imgD[i]['ymax']+self.imgD[i]['ymin'])/2)
                self.imgD[i]['xcenter'] = int((self.imgD[i]['xmax']+self.imgD[i]['xmin'])/2 )
                
    def _SetValuePrintPos(self):
        for i in range(0,251):
            if i in self.imgD:
                #get left x
                self.imgD[i]['xmin'] = self.xPos
                #get bottom y
                self.imgD[i]['ymin'] = self.yPos 
                #get right x
                self.imgD[i]['xmax'] = self.imgD[i]['xmin'] + self.imgD[i]['cols']
                #get top y 
                self.yPos += self.imgD[i]['lins']
                self.imgD[i]['ymax'] = self.yPos
                
                self.imgD[i]['ycenter'] = int((self.imgD[i]['ymax']+self.imgD[i]['ymin'])/2 )
                self.imgD[i]['xcenter'] = int((self.imgD[i]['xmax']+self.imgD[i]['xmin'])/2  ) 
       
    def _SetValuePrintPosR(self):                 
        #ymaxtext = self.imgD[0]['ymax'] - self.legend.frame
        #ymintext = self.imgD[0]['ymin'] + self.legend.frame
        ymaxtext = self.imgD[0]['ymax'] 
        ymintext = self.imgD[0]['ymin'] 
        ytextrange = (ymaxtext-ymintext)/(self.palette.maxLeg-self.palette.minLeg)
        printCenter = self.imgD[0]['ycenter']
        self.rangeCenter = (self.palette.maxLeg-self.palette.minLeg)/2
        if self.legend.compresslabels:
            self.printStep = ytextrange*(printCenter+self.legend.fontsize/2)/(printCenter+self.legend.fontsize)
        else:
            self.printStep = ytextrange*(printCenter+self.legend.fontsize/1)/(printCenter+self.legend.fontsize)
           
           
    def _SetDrawText(self):
        '''20210530, this is  _SetDrawTextOld, can not find _SetDrawText
        '''
        
        
        self.textL = []
        
        for rec in self.palette.items:
                       
            print ('rec',rec)
            print (self.legend.palmin)
            print (self.legend.palmax)
            print (self.scaling.offsetadd)
            print (self.scaling.scalefac)
            
            if rec[0] <= self.legend.palmax and rec[0] >= self.legend.palmin and rec[6] != 'NA':
                
                if self.measure == 'R':

                    if rec[5] == 'auto':
                           
                        if self.scaling.power: 
                                                                      
                            if self.scaling.mirror0:
                                
                                iniVal = rec[0]-125
                                
                                iniVal /= float(self.scaling.scalefac)
                                
                                if iniVal == 0:
                                    
                                    legVal = 0
                                    
                                if iniVal < 0:
                                    
                                    legVal = pow(-iniVal,1/self.scaling.power)
                                    
                                    legVal *= -1
                                    
                                else:
                                    
                                    legVal = pow(iniVal,1/self.scaling.power)
                            else:
                                
                                legVal = int(rec[0])-self.scaling.offsetadd
                                
                                legVal /= float(self.scaling.scalefac)   
                                 
                                #legVal = pow(legVal,1/self.scaling.power)
                        else:
                            
                            legVal = int(rec[0])-self.scaling.offsetadd
                            
                            legVal *= float(self.scaling.scalefac)
                            
                            '''
                            if rec[5].isdigit():
                                
                                legVal = int(rec[0])
                                
                            else:
                                
                                legVal = float(rec[0])
                            '''

                        if self.legend.precision == 0:
                            
                            legStr = '%(s)d' %{'s':legVal}
                            
                        else:
                            precision =  '%(p)dg' %{'p':self.legend.precision}
                            precision = '%.'+precision
                            legStr = '%s' % float(precision % legVal)
                        #SEE https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
                    else: 
                        legStr = rec[5]
 
                    ypos = self.imgD[0]['ycenter'] + (rec[0]-self.palette.minLeg-self.rangeCenter)*self.printStep - (self.legend.fontsize/1.75 + self.legend.framestrokewidth)
 
                else:
                    legStr = rec[5]
                    ypos = self.imgD[rec[0]]['ycenter']- (self.legend.fontsize/1.75 + self.legend.framestrokewidth)
                    SNULLE

                self.textL.append({'txt':legStr, 'ypos':ypos, 'xpos':self.legend.cols+self.legend.buffer[1]+self.legend.textpadding[3]+self.legend.framestrokewidth, 'font':'verdana', 'fontsize':12, 'fill':'black', 'fonteffect':'none'})
            elif rec[0] > 250 and rec[6] != 'NA':
                if rec[0] in self.imgD:
                    ypos = self.imgD[rec[0]]['ycenter']   

                    self.textL.append({'txt':rec[5], 'ypos':ypos, 'xpos':self.legend.cols+self.margin+self.textpadding+self.strokewidth, 'font':'verdana', 'fontsize':12, 'fill':'black', 'fonteffect':'none'})

        if self.measure == 'N' and self.legend.matrix:
            coltext = self.legend.columntext.split(':')
            rowtext = self.legend.rowtext.split(':')

            for c in range(self.legend.columns):
                xpos = self.imgD[self.palette.coreIdL[c]]['xmin']
                ypos = self.imgD[self.palette.coreIdL[c]]['ymax']+self.legend.cols+self.margin+self.textpadding+self.strokewidth
                #self.cv.drawString(xpos, ypos, coltext[c])
                self.textL.append({'txt':rec[5], 'ypos':ypos, 'xpos':xpos, 'font':'verdana', 'fontsize':12, 'fill':'black', 'fonteffect':'none'})

                if c == 1:
                    ypos+= self.legend.fontsize+10
     
                    self.textL.append({'txt':self.legend.columnhead, 'ypos':ypos, 'xpos':self.legend.cols+10, 'font':'verdana', 'fontsize':self.legend.fontsize, 'fill':'black', 'fonteffect':'none'})

                    self.textL.append({'txt':self.legend.rowhead, 'ypos':ypos, 'xpos':10, 'font':'verdana', 'fontsize':self.legend.fontsize, 'fill':'black', 'fonteffect':'none'})

            for c in range(len(rowtext)):
                xpos = 50 #default x position for matrix text
                ypos = self.imgD[self.palette.coreIdL[c]*len(rowtext)]['ycenter']
                #self.cv.drawString(xpos, ypos, rowtext[c])
                self.textL.append({'txt':rowtext[c], 'ypos':ypos, 'xpos':10, 'font':'verdana', 'fontsize':self.legend.fontsize, 'fill':'black', 'fonteffect':'none'})
   
        elif len(self.legend.columnhead) > 0:
            headcols = self.legend.columnhead.split(':')
            headcols.reverse()
            #Add one text padding before printing title
            self.yPos += self.legend.textpadding[2]
            for i,col in enumerate(headcols): 
                self.textL.append({'txt':col, 'ypos':self.yPos, 'xpos':self.legend.textpadding[2], 'font':'verdana', 'fontsize':self.legend.titlefontsize, 'fill':'black', 'fonteffect':'none'})

                #add space after the text as the anchor is below
                self.yPos += self.legend.titlefontsize*1.33
                self.yPos += self.legend.textpadding[0]                 
    
    def _CanvasDrawImages(self):
        '''
        '''
        paletteRange = self.palette.maxLeg+1-self.palette.minLeg
        #print ('self.palette.minLeg',self.palette.minLeg)
        #print ('self.palette.maxLeg',self.palette.maxLeg)

        for item in self.imgD:
            if self.imgD[item]['typ'] == 'gradientfill':
        
                # create a new linearGradient element
                vertical_gradient = self.dwg.linearGradient((0, 0), (0, 1))
        
                # add gradient to the defs section of the drawing
                self.dwg.defs.add(vertical_gradient)

                # define the gradient 
                prevkey = False
                for key in self.svgPalette:
                    if prevkey:
                        i = 0.99999*(1-float(key)/float(paletteRange))
                        vertical_gradient.add_stop_color(i, self.svgPalette[prevkey])
                        #print ('svgpalette', key, self.svgPalette[key],i)
                    if paletteRange < 50:
                        prevkey = key
                    #Gradient drawing is inverted compared to the PNG
                    i = 1-float(key)/float(paletteRange)
                    #print ('svgpalette', key, self.svgPalette[key],i)
                    vertical_gradient.add_stop_color(i, self.svgPalette[key])
                    
                vertical_gradient.add_stop_color(1, self.svgPalette[key])
                x0 = self.imgD[item]['xmin']*self.scalefac
                y0 = self.height-self.imgD[item]['ymax']*self.scalefac
                x1 = (self.imgD[item]['xmax']*self.scalefac)-x0
                y1 = self.height-(self.imgD[item]['ymin']*self.scalefac)-y0
                if self.legend.framestrokewidth:
                    self.dwg.add(self.dwg.rect( (x0,y0), 
                                (x1,y1), fill=vertical_gradient.get_paint_server(default='currentColor'),stroke='black', stroke_width=self.legend.framestrokewidth))
                else:
                    self.dwg.add(self.dwg.rect( (x0,y0), 
                                (x1,y1), fill=vertical_gradient.get_paint_server(default='currentColor')))

            else:
                SNULLEBULLE
    
    
    def _CanvasDrawText(self): 
        
        paragraph = self.dwg.add(self.dwg.g(font_size=self.legend.fontsize))
        
        for txt in self.textL:

            fontsize = txt['fontsize']*self.fontfac
            #print (txt['txt'], txt['xpos']*self.scalefac, self.height-txt['ypos']*self.scalefac, txt['fill'], fontsize)
            paragraph.add(self.dwg.text(txt['txt'], (txt['xpos']*self.scalefac, self.height-txt['ypos']*self.scalefac), 
                                        fill = txt['fill'], font_size=fontsize))
            '''
            fs = [8,10,12,14,16]
            ypos = 10
            for f in fs:
                ypos += f
                txt = '%(f)d' %{'f':f}
                paragraph.add(self.dwg.text(txt, (120, ypos), 
                                        fill = 'black', font_size=f*1.33))
            '''
      
    def _DwgToPng(self, svgFPN, pngFPN, jpgFPN):
        '''ImageMagick does not work, but inkscape does
        ''' 
        
        params = {'w':self.legend.pngwidth,'h':self.legend.pngheight,
                  'color': self.pp.process.parameters.legendbackground,
                  'opacity': self.pp.process.parameters.legendopacity,
                      'src':svgFPN, 'dst':pngFPN}
            
        magickCmd = 'convert -density 96 -resize %(w)dx%(h)d! ' %params
        '''
        if cropL:
            magickCmd += '-crop %(cw)dx%(ch)d+%(cx)d+%(cy)d ' %params
        '''
        magickCmd += ' %(src)s ' %params
        '''
        if border:
            magickCmd += '\( -border %(b)dx%(b)d -bordercolor %(bc)s \) ' %params
        '''
        magickCmd += '%(dst)s' %params
        #print (magickCmd)
        #subprocess.call('/usr/local/bin/' + magickCmd, shell=True)
        #os.system('/usr/local/bin/' + magickCmd)
    
        #iscmd = 'inkscape -D -z -e %(dst)s -w %(w)d -h %(h)d %(src)s' %params
        iscmd = 'inkscape --export-filename=%(dst)s --export-area-drawing\
            --export-background=%(color)s --export-background-opacity=%(opacity)d %(src)s' %params

        #os.system('/usr/local/bin/' + iscmd )
        
        
        print ('/Applications/Inkscape.app/Contents/MacOS/' + iscmd )
        
        os.system('/Applications/Inkscape.app/Contents/MacOS/' + iscmd )
        
        #produce jpg if requested
        if self.pp.process.parameters.jpg:
            params = {'src':pngFPN, 'dst':jpgFPN, 'q':self.pp.process.parameters.jpg}
            magickCmd = 'convert %(src)s -quality %(q)d %(dst)s ' %params
            subprocess.call('/usr/local/bin/' + magickCmd, shell=True)
                  
    def _MovieClock(self):
        '''
        '''
        exitstr = 'layout.layout.ProcessLaout._MovieClock not yet implemented'
        
        exit (exitstr)

        