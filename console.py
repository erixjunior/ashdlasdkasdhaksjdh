#!/usr/bin/env python3
"""
Console - Static Logging Class
Provides colored console output with different log levels
Similar to JavaScript console with Python implementation
"""

import sys
from datetime import datetime
from typing import Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration with priority order"""

    DEBUG = ("DEBUG", 0)
    LOG = ("LOG", 1)
    INFO = ("INFO", 2)
    SUCCESS = ("SUCCESS", 3)
    WARNING = ("WARNING", 4)
    ERROR = ("ERROR", 5)

    def __init__(self, level_name, priority):
        self.level_name = level_name
        self.priority = priority


class Colors:
    """ANSI color codes for console output"""

    # Reset
    RESET = "\033[0m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"


class Console:
    """
    Static Console class for colored logging output
    Provides different log levels with appropriate colors and formatting
    """

    # Configuration
    _show_timestamp = True
    _show_level = True
    _enabled = True
    _current_log_level = LogLevel.DEBUG  # Default to show all logs

    @staticmethod
    def _get_log_level_from_env():
        """Get log level from environment configuration"""
        try:
            from config import Env

            level_str = getattr(Env, "LOG_LEVEL", "DEBUG")

            # Map string to LogLevel enum
            level_map = {
                "DEBUG": LogLevel.DEBUG,
                "LOG": LogLevel.LOG,
                "INFO": LogLevel.INFO,
                "SUCCESS": LogLevel.SUCCESS,
                "WARNING": LogLevel.WARNING,
                "ERROR": LogLevel.ERROR,
            }

            return level_map.get(level_str, LogLevel.DEBUG)
        except Exception:
            # If config not available, default to DEBUG
            return LogLevel.DEBUG

    @staticmethod
    def _should_log(level: LogLevel) -> bool:
        """Check if message should be logged based on current log level"""
        if not hasattr(Console, "_log_level_initialized"):
            Console._current_log_level = Console._get_log_level_from_env()
            Console._log_level_initialized = True

        return level.priority >= Console._current_log_level.priority

    @staticmethod
    def _format_message(level: LogLevel, *args, **kwargs) -> str:
        """Format message with timestamp and level"""
        # Convert all arguments to string
        message_parts = []
        for arg in args:
            if isinstance(arg, str):
                message_parts.append(arg)
            else:
                message_parts.append(str(arg))

        message = " ".join(message_parts)

        # Add timestamp if enabled
        timestamp = ""
        if Console._show_timestamp:
            now = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
            timestamp = f"[{now}] "

        # Add level if enabled
        level_str = ""
        if Console._show_level:
            level_str = f"[{level.level_name}] "

        return f"{timestamp}{level_str}{message}"

    @staticmethod
    def _print_colored(color: str, level: LogLevel, *args, **kwargs) -> None:
        """Print colored message to console"""
        if not Console._enabled or not Console._should_log(level):
            return

        formatted_message = Console._format_message(level, *args, **kwargs)
        colored_message = f"{color}{formatted_message}{Colors.RESET}"

        # Print to stderr for errors and warnings, stdout for others
        output = (
            sys.stderr if level in [LogLevel.ERROR, LogLevel.WARNING] else sys.stdout
        )
        print(colored_message, file=output)

    @staticmethod
    def log(*args, **kwargs) -> None:
        """Regular log message (white/default color)"""
        Console._print_colored(Colors.WHITE, LogLevel.LOG, *args, **kwargs)

    @staticmethod
    def debug(*args, **kwargs) -> None:
        """Debug message (cyan color, dimmed)"""
        if not Console._enabled or not Console._should_log(LogLevel.DEBUG):
            return

        formatted_message = Console._format_message(LogLevel.DEBUG, *args, **kwargs)
        colored_message = f"{Colors.CYAN}{Colors.DIM}{formatted_message}{Colors.RESET}"
        print(colored_message, file=sys.stdout)

    @staticmethod
    def info(*args, **kwargs) -> None:
        """Info message (blue color)"""
        Console._print_colored(Colors.BRIGHT_BLUE, LogLevel.INFO, *args, **kwargs)

    @staticmethod
    def success(*args, **kwargs) -> None:
        """Success message (green color)"""
        Console._print_colored(Colors.BRIGHT_GREEN, LogLevel.SUCCESS, *args, **kwargs)

    @staticmethod
    def warning(*args, **kwargs) -> None:
        """Warning message (yellow color, bold)"""
        if not Console._enabled or not Console._should_log(LogLevel.WARNING):
            return

        formatted_message = Console._format_message(LogLevel.WARNING, *args, **kwargs)
        colored_message = (
            f"{Colors.YELLOW}{Colors.BOLD}⚠️  {formatted_message}{Colors.RESET}"
        )
        print(colored_message, file=sys.stderr)

    @staticmethod
    def error(*args, **kwargs) -> None:
        """Error message (red color, bold)"""
        if not Console._enabled or not Console._should_log(LogLevel.ERROR):
            return

        formatted_message = Console._format_message(LogLevel.ERROR, *args, **kwargs)
        colored_message = (
            f"{Colors.BRIGHT_RED}{Colors.BOLD}❌ {formatted_message}{Colors.RESET}"
        )
        print(colored_message, file=sys.stderr)

    @staticmethod
    def clear() -> None:
        """Clear console screen"""
        import os

        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def group(label: str = "") -> None:
        """Start a console group (similar to console.group in JS)"""
        Console._print_colored(Colors.BRIGHT_MAGENTA, LogLevel.LOG, f"▼ {label}")

    @staticmethod
    def group_end() -> None:
        """End console group"""
        Console._print_colored(Colors.BRIGHT_MAGENTA, LogLevel.LOG, "▲")

    @staticmethod
    def table(data: Any) -> None:
        """Display data in table format"""
        try:
            if isinstance(data, dict):
                Console._print_colored(Colors.CYAN, LogLevel.LOG, "📊 Table:")
                for key, value in data.items():
                    Console._print_colored(
                        Colors.WHITE, LogLevel.LOG, f"  {key}: {value}"
                    )
            elif isinstance(data, list):
                Console._print_colored(Colors.CYAN, LogLevel.LOG, "📊 Array:")
                for i, item in enumerate(data):
                    Console._print_colored(
                        Colors.WHITE, LogLevel.LOG, f"  [{i}]: {item}"
                    )
            else:
                Console._print_colored(Colors.WHITE, LogLevel.LOG, f"📊 {data}")
        except Exception as e:
            Console.error(f"Error displaying table: {e}")

    @staticmethod
    def time(label: str = "default") -> None:
        """Start timer (similar to console.time in JS)"""
        if not hasattr(Console, "_timers"):
            Console._timers = {}
        Console._timers[label] = datetime.now()
        Console._print_colored(
            Colors.BRIGHT_CYAN, LogLevel.LOG, f"⏱️  Timer '{label}' started"
        )

    @staticmethod
    def time_end(label: str = "default") -> None:
        """End timer and display elapsed time"""
        if not hasattr(Console, "_timers") or label not in Console._timers:
            Console.warning(f"Timer '{label}' not found")
            return

        start_time = Console._timers[label]
        elapsed = datetime.now() - start_time
        elapsed_ms = elapsed.total_seconds() * 1000

        Console._print_colored(
            Colors.BRIGHT_CYAN, LogLevel.LOG, f"⏱️  Timer '{label}': {elapsed_ms:.2f}ms"
        )
        del Console._timers[label]

    @staticmethod
    def separator(char: str = "=", length: int = 50) -> None:
        """Print separator line"""
        Console._print_colored(Colors.DIM, LogLevel.LOG, char * length)

    # Configuration methods
    @staticmethod
    def set_timestamp(enabled: bool) -> None:
        """Enable/disable timestamp in logs"""
        Console._show_timestamp = enabled

    @staticmethod
    def set_level_display(enabled: bool) -> None:
        """Enable/disable level display in logs"""
        Console._show_level = enabled

    @staticmethod
    def set_enabled(enabled: bool) -> None:
        """Enable/disable all console output"""
        Console._enabled = enabled

    @staticmethod
    def set_log_level(level: LogLevel) -> None:
        """Set the minimum log level to display"""
        Console._current_log_level = level
        Console._log_level_initialized = True

    @staticmethod
    def get_log_level() -> LogLevel:
        """Get current log level"""
        if not hasattr(Console, "_log_level_initialized"):
            Console._current_log_level = Console._get_log_level_from_env()
            Console._log_level_initialized = True
        return Console._current_log_level

    # Aliases for common use cases
    @staticmethod
    def warn(*args, **kwargs) -> None:
        """Alias for warning"""
        Console.warning(*args, **kwargs)

    @staticmethod
    def err(*args, **kwargs) -> None:
        """Alias for error"""
        Console.error(*args, **kwargs)
