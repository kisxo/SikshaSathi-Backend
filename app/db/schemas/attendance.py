import enum

class AttendanceModeChoice(enum.Enum):
    online = "Online"
    offline = "Offline"
    def __str__(self) -> str:
        return self.value