import logging as _logging
import os
from datetime import datetime
from config import Settings

# Create logs directory next to this file
dir_path = os.path.dirname(__file__)
logs_dir = os.path.join(dir_path, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Log file with timestamp
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file = os.path.join(logs_dir, f'log_{timestamp}.log')

# Configure logger
logger = _logging.getLogger('arknights')
logger.setLevel(_logging.DEBUG)

# File handler
file_handler = _logging.FileHandler(log_file)
file_handler.setLevel(getattr(_logging, Settings.logging.file_level.upper(), _logging.DEBUG))

# Console handler
console_handler = _logging.StreamHandler()
console_handler.setLevel(getattr(_logging, Settings.logging.console_level.upper(), _logging.INFO))

# Format strings include module and function for better context
_BASE_FMT = '%(asctime)s - %(name)s - %(levelname)s - [%(module)s] [%(funcName)s] - %(message)s'

# File formatter (no colors)
file_formatter = _logging.Formatter(_BASE_FMT)
file_handler.setFormatter(file_formatter)

# Console formatter with module-based coloring
class _ModuleColorFormatter(_logging.Formatter):
    RESET = '\x1b[0m'
    # Colors
    DIM = '\x1b[90m'            # utils (least important)
    MID = '\x1b[36m'            # other modules (level 2)
    HIGH = '\x1b[93m'           # scenarios (most important)

    def format(self, record: _logging.LogRecord) -> str:
        # Choose color based on source module
        module = getattr(record, 'module', '')
        if module == 'utils':
            color = self.DIM
        elif module == 'scenarios':
            color = self.HIGH
        else:
            color = self.MID
        base = super().format(record)
        return f"{color}{base}{self.RESET}"

try:
    # Enable ANSI colors on Windows terminals when available
    import colorama  # type: ignore
    try:
        colorama.just_fix_windows_console()
    except Exception:
        pass
except Exception:
    pass

console_formatter = _ModuleColorFormatter(_BASE_FMT)
console_handler.setFormatter(console_formatter)

# --- Runtime controls ---
_LEVEL_NAMES = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

def set_console_level(level_name: str):
    lvl = getattr(_logging, level_name.upper(), None)
    if lvl is None:
        return
    console_handler.setLevel(lvl)
    # update config snapshot
    from dataclasses import replace
    Settings.logging = replace(Settings.logging, console_level=level_name.upper())

def set_file_level(level_name: str):
    lvl = getattr(_logging, level_name.upper(), None)
    if lvl is None:
        return
    file_handler.setLevel(lvl)
    from dataclasses import replace
    Settings.logging = replace(Settings.logging, file_level=level_name.upper())

def get_console_level() -> str:
    lvl = console_handler.level
    for name in _LEVEL_NAMES:
        if getattr(_logging, name) == lvl:
            return name
    return str(lvl)

def get_file_level() -> str:
    lvl = file_handler.level
    for name in _LEVEL_NAMES:
        if getattr(_logging, name) == lvl:
            return name
    return str(lvl)

def set_logging_enabled(enabled: bool):
    # Efficiently enable/disable output without removing handlers
    if enabled:
        console_handler.addFilter(lambda record: True)
        file_handler.addFilter(lambda record: True)
    else:
        console_handler.addFilter(lambda record: False)
        file_handler.addFilter(lambda record: False)
    from dataclasses import replace
    Settings.logging = replace(Settings.logging, enabled=bool(enabled))

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
