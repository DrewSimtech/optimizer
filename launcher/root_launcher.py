
# global package imports
import os
import shutil


# Class definition
class RootLauncher(object):
    '''Interface for the launcher class.
    Sends out runs.'''
    card_name_layout = '{0._data_dir}/step{0._run_number:0>3}/'
    card_name_layout += '{0._base_file_trimmed}_{gradient}.CRD'
    run_name_in_dir = '{run_dir}/{this._base_file_trimmed}_{gradient}.CRD'
    mutable_data_layout = '{name} = {value}\n'

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
        self._cards_to_launch = []
        super().__init__(**kwargs)

    #############################################
    # UTILITY FUNCTIONS                         #
    #############################################
    def getDirNameFromRunName(self, run_name):
        assert not hasattr(super(), 'getDirNameFromRunName')
        dir_name = run_name.rpartition('/')[0]
        return dir_name

    def getRunNameInDirForMutable(self, run_dir, mutable, slope=''):
        assert not hasattr(super(), 'getRunNameInDirForMutable')
        gradient = str(mutable.name)
        if(slope):
            gradient += str(slope)
        run_name = self.run_name_in_dir.format(
            run_dir=run_dir, this=self, gradient=gradient)
        print(run_name)
        return run_name

    #############################################
    # CREATE RUN DATA                           #
    #############################################
    def getLatestRunset(self):
        assert not hasattr(super(), 'getLatestRunset')
        return self._cards_to_launch

    def createRuns(self, mutables, num_runs=10):
        assert not hasattr(super(), 'createRuns')
        self._card_files = []
        for i in range(num_runs):
            self._run_number += 1
            self._writeStepCard(i, mutables)
            for m in mutables:
                self._writeGradientCard(i, mutables, m)

    def _getCardPath(self, gradient):
        assert not hasattr(super(), '_getCardPath')
        card_path = self.card_name_layout.format(self, gradient=gradient)

        # Make the folder if it doesn't exist.
        card_dir = card_path.rpartition('/')[0]
        if(not os.access(card_dir, os.R_OK)):
            os.makedirs(card_dir)
        # Return the name
        return card_path

    def _writeStepCard(self, step, mutables):
        assert not hasattr(super(), '_writeStepCard')
        # Set up a new card name
        card_path = self._getCardPath('all')
        # Copy the base information into it
        shutil.copyfile(self._card_base_path, card_path)
        # Write the changed information into it
        self._writeMutablesToCard(
            card_path, step, mutables, None, 0.0)
        # Add it to our launch list
        self._cards_to_launch.append(card_path)

    def _writeGradientCard(self, step, mutables, cur_mutable):
        assert not hasattr(super(), '_writeGradientCard')
        # Create and write out a card with a positive gradient.
        plus_card_path = self._getCardPath(cur_mutable.name + "_plus")
        shutil.copyfile(self._card_base_path, plus_card_path)
        self._writeMutablesToCard(
            plus_card_path, step, mutables, cur_mutable, 1.0)
        # Add it to our launch list
        self._cards_to_launch.append(plus_card_path)

        # Create and write out a card with a negative gradient.
        # these two gradients combined will combine to get the slope
        minus_card_path = self._getCardPath(cur_mutable.name + "_minus")
        shutil.copyfile(self._card_base_path, minus_card_path)
        self._writeMutablesToCard(
            minus_card_path, step, mutables, cur_mutable, -1.0)
        # Add it to our launch list
        self._cards_to_launch.append(minus_card_path)

    def _writeMutablesToCard(self, card_path, step, mutables,
                             cur_mutable=None, slope=0.0):
        assert not hasattr(super(), '_writeMutablesToCard')
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
    def launch(self):
        assert not hasattr(super(), 'launch')
