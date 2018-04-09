
# global package imports
import os
import shutil
# local package imports
from debug import Debug, rootClassMethod


# Class definition
class RootLauncher(object):
    '''Interface for the launcher class.
    Sends out runs.'''
    card_name_layout = '{0._data_dir}/step{0._run_number:0>3}/'
    card_name_layout += '{0._base_file_trimmed}_{gradient}.CRD'
    run_name_in_dir = '{run_dir}/{this._base_file_trimmed}_{gradient}.CRD'
    mutable_data_layout = '{name} = {value}\n'
    cur_iter_archive = '{0._data_dir}/step_map/iteration_{0._iterations}'

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, base_file, data_dir, num_steps=10, **kwargs):
        self._base_file = base_file
        self._base_file_trimmed = base_file.rpartition('.')[0]  # trim filetype
        self._data_dir = data_dir
        self._card_base_path = os.path.join(self._data_dir, self._base_file)
        self._num_steps = 10
        self._run_number = 0
        self._iterations = 0
        self._cards_to_launch = []
        super().__init__(**kwargs)

    #############################################
    # UTILITY FUNCTIONS                         #
    #############################################
    @rootClassMethod
    def getDirNameFromRunName(self, run_name):
        dir_name = run_name.rpartition('/')[0]
        return dir_name

    @rootClassMethod
    def getRunNameInDirForMutable(self, run_dir, mutable, slope=''):
        gradient = str(mutable.name)
        if(slope):
            gradient += str(slope)
        run_name = self.run_name_in_dir.format(
            run_dir=run_dir, this=self, gradient=gradient)
        Debug.log(run_name)
        return run_name

    @rootClassMethod
    def getStepFromRunName(self, run_name):
        for item in run_name.split('/'):
            if('step' in item):
                step = int(item.strip('step'))
                return step

    @rootClassMethod
    def archiveDir(self, dir_name):
        shutil.move(dir_name, self.cur_iter_archive.format(self))

    @rootClassMethod
    def getLatestRunset(self):
        return self._cards_to_launch

    #############################################
    # CREATE RUN DATA                           #
    #############################################
    @rootClassMethod
    def _clearRunData(self):
        # rmtree is dangerous cause it will remove the folder and
        # all of its contents. So be careful with what we remove.
        # Don't want to accedently clean an entire folder of code.
        for run in self._cards_to_launch:
            # check for data before we attempt delete.
            if (os.access(run, os.R_OK)):
                del_dir = self.getDirNameFromRunName(run)
                Debug.log('del: ' + str(del_dir))
                shutil.rmtree(del_dir)

    @rootClassMethod
    def createRuns(self, mutables, num_runs=10):
        # clear launch set before building the next ones
        self.clearRunData()
        for i in range(num_runs):
            self._run_number += 1
            self._populateCard(i, mutables, None, 'all', 0.0)
            for m in mutables:
                self._populateCard(i, mutables, m, m.name + '_plus', 1.0)
                self._populateCard(i, mutables, m, m.name + '_minus', -1.0)

    @rootClassMethod
    def _populateCard(self, step, mutables, cur_mutable, gradient, slope):
        # Set up a new card name
        card_path = self._getCardPath(gradient)
        # Copy the base information into it
        shutil.copyfile(self._card_base_path, card_path)
        # Write the changed information into it
        self._writeMutablesToCard(
            card_path, step, mutables, cur_mutable, slope)
        # Add it to our launch list
        self._cards_to_launch.append(card_path)

    @rootClassMethod
    def _getCardPath(self, gradient):
        card_path = self.card_name_layout.format(self, gradient=gradient)
        # Make the folder if it doesn't exist.
        card_dir = card_path.rpartition('/')[0]
        if(not os.access(card_dir, os.R_OK)):
            os.makedirs(card_dir)
        # Return the name
        return card_path

    @rootClassMethod
    def _writeMutablesToCard(self, card_path, step, mutables,
                             cur_mutable=None, slope=0.0):
        # Calculate the gradient. by default it's 0 and
        # doesnt change the input.
        gradient_width = 0.0
        if (cur_mutable):
            gradient_width = cur_mutable.getGradientWidthAtStep(step) * slope
        # Write each of the mutables to the card excepting the current one
        # if were calculating slope.
        with open(card_path, 'a') as f:
            for m in mutables:
                if (cur_mutable and m == cur_mutable):
                    f.write(self.mutable_data_layout.format(
                        name=m.name,
                        value=m.getValueAtStep(step) + gradient_width,
                    ))
                else:
                    f.write(self.mutable_data_layout.format(
                        name=m.name,
                        value=m.getValueAtStep(step),
                    ))

    #############################################
    # LAUNCH RUNS                               #
    #############################################
    @rootClassMethod
    def launch(self):
        # implement in child classes
        pass

