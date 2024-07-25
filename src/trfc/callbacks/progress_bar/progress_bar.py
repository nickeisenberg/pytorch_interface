from tqdm import tqdm

from .base import ProgressBar as _ProgressBar
from ...trainer import Trainer


def tqdm_postfix_to_dictionary(postfix: str):
    return dict([x.strip().split("=") for x in postfix.split(",")]) if postfix else {}

def append_tqdm_postfix(pbar: tqdm, **kwargs):
    pbar.set_postfix(
        {**tqdm_postfix_to_dictionary(pbar.postfix), **{k: v for k, v in kwargs.items()}}
    )

class ProgressBar(_ProgressBar):
    """The progress bar"""

    def __init__(self, log_to_bar_every: int = 100):
        super().__init__()
        
        self.log_to_bar_every = log_to_bar_every

        self._postfix = {}
        self._train_progress_bar = None
        self._validation_progress_bar = None
    
    @property
    def postfix(self):
        return self._postfix
    
    @postfix.setter
    def postfix(self, postfix_dict: dict):
        if isinstance(postfix_dict, dict):
            self._postfix = postfix_dict
        else:
            raise Exception("ERROR: postfix_dict must be a dict[str, value]")

    @property
    def train_progress_bar(self) -> tqdm:
        if self._train_progress_bar is None:
            raise Exception("ERROR: train_progress_bar called before being set.")
        return self._train_progress_bar

    @train_progress_bar.setter
    def train_progress_bar(self, pbar: tqdm):
        if isinstance(pbar, tqdm):
            self._train_progress_bar = pbar
        else:
            raise Exception("ERROR: pbar must be a tqdm")

    @property
    def validation_progress_bar(self) -> tqdm:
        if self._validation_progress_bar is None:
            raise Exception("ERROR: validation_progress_bar called before set")
        return self._validation_progress_bar

    @validation_progress_bar.setter
    def validation_progress_bar(self, pbar: tqdm):
        if isinstance(pbar, tqdm):
            self._validation_progress_bar = pbar
        else:
            raise Exception("ERROR: pbar must be a tqdm")

    def log(self, name, value):
        """Log values intra batch to be displayed to the tqdm bar"""
        self.postfix[name] = value

    def before_train_epoch_pass(self, trainer: Trainer):
        self.train_progress_bar = tqdm(trainer.variables.train_loader, leave=True)

    def before_validation_epoch_pass(self, trainer: Trainer):
        self.validation_progress_bar = tqdm(trainer.variables.validation_loader, leave=True)

    def after_train_batch_pass(self, trainer: Trainer) -> None:
        if trainer.variables.current_batch_idx % self.log_to_bar_every == 0:
            append_tqdm_postfix(self.train_progress_bar, **self.postfix)
        self.postfix = {}

    def after_validation_batch_pass(self, trainer: Trainer) -> None:
        if self.validation_progress_bar is not None:
            if trainer.variables.current_batch_idx % self.log_to_bar_every == 0:
                append_tqdm_postfix(self.validation_progress_bar, **self.postfix)
            self.postfix = {}
