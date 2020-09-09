# Copyright 2019 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os,sys
import pandas as pd

class LogFile(object):
    """Scrape SOWFA log file for simulation information and store in a
    pandas dataframe.
    """
    def __init__(self, fpath):
        self._read(fpath)

    def _read(self, fpath):
        if not os.path.isfile(fpath):
            sys.exit(fpath,'not found')
        startedTimeLoop = False
        times = []
        dt = []
        CoMean = []
        CoMax = []
        contErrMin = []
        contErrMax = []
        contErrMean = []
        bndryFluxTot = []
        with open(fpath,'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('Create mesh'):
                    startTime = float(line.split()[-1])
                    print('Simulation start from t=',startTime)
                elif line.startswith('Starting time loop'):
                    startedTimeLoop = True
                if not startedTimeLoop:
                    continue
                if line.startswith('Time ='):
                    # Time = 0.5  Time Step = 1
                    curTime = float(line.split()[2])
                    times.append(curTime)
                elif line.startswith('deltaT'):
                    # deltaT = 0.5
                    dt.append(float(line.split()[2]))
                elif line.startswith('Courant Number'):
                    # Courant Number mean: 0.25 max: 0.25
                    line = line.split()
                    CoMean.append(float(line[3]))
                    CoMax.append(float(line[5]))
                elif line.startswith('minimum:'):
                    # -Local Cell Continuity Error:
                    #     minimum: 4.78677122625e-18
                    #     maximum: 4.1249975169e-10
                    #     weighted mean: 1.55849978382e-12
                    contErrMin.append(float(line.split()[1]))
                elif line.startswith('maximum:'):
                    contErrMax.append(float(line.split()[1]))
                elif line.startswith('weighted mean:'):
                    contErrMean.append(float(line.split()[2]))
                elif line.startswith('total - flux:'):
                    # -Boundary Flux:
                    #     lower - flux: 0  / area: 1000000
                    #     upper - flux: -3.40510497274e-19 / area: 1000000
                    #     west - flux: -4972611.5  / area: 500000
                    #     east - flux: 4971897.53527   / area: 500000
                    #     north - flux: 49044.2606921  / area: 500000
                    #     south - flux: -48330.2959591 / area: 500000
                    #     total - flux: 3.52156348526e-09  / area: 4000000
                    bndryFluxTot.append(float(line.split()[3]))
        self.df = pd.DataFrame(
                data={
                    'deltaT': dt,
                    'CoMean': CoMean,
                    'CoMax': CoMax,
                    'continuityErrorMin': contErrMin,
                    'continuityErrorMax': contErrMax,
                    'continuityErrorWeightedMean': contErrMean,
                    'boundaryFluxTotal': bndryFluxTot,
                },
                index=pd.Index(times, name='time'))

#------------------------------------------------------------------------------
if __name__ == '__main__':
    df = pd.concat([LogFile(fpath).df for fpath in sys.argv[1:]])
    df.to_csv('log.csv')