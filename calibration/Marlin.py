
import os
import subprocess
from calibration.XmlTools import etree
import logging
import tempfile
from calibration.MarlinXML import MarlinXML
import time

""" Marlin class.
"""
class Marlin(object) :
    """ Constructor
    """
    def __init__(self, steeringFile=None) :
        self._marlinXML = MarlinXML()
        self._logger = logging.getLogger("marlin")

        # set steering file and load it
        if steeringFile is not None :
            self._marlinXML.setSteeringFile(steeringFile, True)

    """ Load processor parameters from a xml tree
        Usage : loadParameter(xmlTree, "//input")
    """
    def loadParameters(self, xmlTree, path):
        self._marlinXML.loadParameters(xmlTree, path)

    """ Load step output parameters
    """
    def loadStepOutputParameters(self, xmlTree, stepName):
        self._marlinXML.loadStepOutputParameters(xmlTree, stepName)

    """ Load input parameters
    """
    def loadInputParameters(self, xmlTree):
        self._marlinXML.loadInputParameters(xmlTree)

    """ Set a processor parameter.
    """
    def setProcessorParameter(self, processor, parameter, value) :
        self._marlinXML.setProcessorParameter(processor, parameter, value)

    """ Get a processor parameter.
    """
    def getProcessorParameter(self, processor, parameter):
        return self._marlinXML.getProcessorParameter(processor, parameter)

    """ Set the marlin steering file
    """
    def setSteeringFile(self, steeringFile, load=False) :
        self._marlinXML.setSteeringFile(steeringFile, load)

    """ Set the lcio input file(s)
        String list or string accepted
    """
    def setInputFiles(self, inputFiles) :
        self._marlinXML.setInputFiles(inputFiles)

    """ Set the GEAR file
    """
    def setGearFile(self, gearFile) :
        self._marlinXML.setGearFile(gearFile)

    """ Set the compact file
    """
    def setCompactFile(self, compactFile):
        self._marlinXML.setCompactFile(compactFile)

    """ Set the Pfo analysis root output file name
    """
    def setPfoAnalysisOutput(self, rootOutput):
        self._marlinXML.setPfoAnalysisOutput(rootOutput)

    """ Set the number of events to skip
    """
    def setSkipNEvents(self, nEvents) :
        self._marlinXML.setSkipNEvents(nEvents)

    """ Set the global verbosity
    """
    def setVerbosity(self, verbosity) :
        self._marlinXML.setVerbosity(verbosity)

    """ Set the max number of records to process (runs + events)
    """
    def setMaxRecordNumber(self, maxRecordNumber) :
        self._marlinXML.setMaxRecordNumber(maxRecordNumber)

    """ Set the global random seed
    """
    def setRandomSeed(self, randomSeed) :
        self._marlinXML.setRandomSeed(randomSeed)

    """ Run the marlin process using Popen function of subprocess module
    """
    def run(self) :
        args = self.createProcessArgs()
        self._logger.info("Marlin command line : " + " ".join(args))
        process = subprocess.Popen(args = args)
        if process.wait() :
            raise RuntimeError
        self._logger.info("Marlin ended with status 0")

    """ Create the marlin process command line argument (Marlin + args)
    """
    def createProcessArgs(self) :
        args = ['Marlin']
        # generate temporary steering file for running marlin
        tmpSteeringFile = self._marlinXML.writeTmp(False)
        print "Wrote marlin xml file in " + tmpSteeringFile
        args.append(tmpSteeringFile)
        return args

    """ Turn off the target list of processors
        This method removes entries in the <execute> marlin xml element
    """
    def turnOffProcessors(self, processors) :
        self._marlinXML.turnOffProcessors(processors)

    """ Turn off all processors except the ones ine the spcified list
        This method removes entries in the <execute> marlin xml element
    """
    def turnOffProcessorsExcept(self, processors) :
        self._marlinXML.turnOffProcessorsExcept(processors)


################################################################################

""" ParallelMarlin class.

    Run multiple instances of marlin in parallel (process)
    Use setMaxNParallelInstances(n) to decide how many instance
    can be run in parallel, addMarlinInstance(marlin) to add a marlin
    instance and run() to process
"""
class ParallelMarlin(object):
    def __init__(self):
        self._marlinInstances = []
        self._maxNParallelInstances = 3

    """ Load processor parameters from a xml tree
        Usage : loadParameter(xmlTree, "//input")
    """
    def loadParameters(self, xmlTree, path):
        for m in self._marlinInstances:
            m.loadParameters(xmlTree, path)

    """ Load step output parameters
    """
    def loadStepOutputParameters(self, xmlTree, stepName):
        for m in self._marlinInstances:
            m.loadStepOutputParameters(xmlTree, stepName)

    """ Load input parameters
    """
    def loadInputParameters(self, xmlTree):
        for m in self._marlinInstances:
            m.loadInputParameters(xmlTree)

    """ Add a marlin instance to run in parallel
    """
    def addMarlinInstance(self, marlin):
        if isinstance(marlin, Marlin):
            self._marlinInstances.append(marlin)

    """ Set the maximum number of concurrent marlin instance to run
    """
    def setMaxNParallelInstances(self, maxInstances):
        if maxInstances > 0 :
            self._maxNParallelInstances = maxInstances

    """ Run the registered marlin concurrently
    """
    def run(self):
        marlinQueue = list(self._marlinInstances)
        runningMarlinInstances = {}
        marlinEndStatus = {m : None for m in marlinQueue}

        while 1:

            if len(marlinQueue) == 0 and len(runningMarlinInstances) == 0:
                break

            if len(runningMarlinInstances) < self._maxNParallelInstances and len(marlinQueue):
                marlin = marlinQueue.pop(0)
                args = marlin.createProcessArgs()
                process = subprocess.Popen(args = args)
                runningMarlinInstances[process] = marlin
            else:
                time.sleep(1)

            for proc, marlin in runningMarlinInstances.items():
                status = proc.poll()
                if status is not None :
                    marlinEndStatus[marlin] = status
                    del runningMarlinInstances[proc]

        print "ParallelMarlin ended with the following status ({0} instances):".format(len(marlinEndStatus))
        for marlin, status in marlinEndStatus.items():
            print "  -> {0} ended with status {1}".format(marlin, status)






#
