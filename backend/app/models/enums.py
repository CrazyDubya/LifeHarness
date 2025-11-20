import enum


class RelationshipStatus(str, enum.Enum):
    SINGLE = "single"
    PARTNERED = "partnered"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    COMPLICATED = "complicated"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class MainRole(str, enum.Enum):
    STUDENT = "student"
    EMPLOYEE = "employee"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    CAREGIVER = "caregiver"
    OTHER = "other"


class IntensityLevel(str, enum.Enum):
    LIGHT = "light"
    BALANCED = "balanced"
    DEEP = "deep"


class TimeBucket(str, enum.Enum):
    PRE10 = "pre10"
    TENS = "10s"
    TWENTIES = "20s"
    THIRTIES = "30s"
    FORTIES = "40s"
    FIFTY_PLUS = "50plus"


class TopicBucket(str, enum.Enum):
    FAMILY_OF_ORIGIN = "family_of_origin"
    FRIENDSHIPS = "friendships"
    ROMANTIC_LOVE = "romantic_love"
    CHILDREN = "children"
    WORK_CAREER = "work_career"
    MONEY_STATUS = "money_status"
    HEALTH_BODY = "health_body"
    CREATIVITY_PLAY = "creativity_play"
    BELIEFS_VALUES = "beliefs_values"
    CRISES_TURNING_POINTS = "crises_turning_points"


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"


class VisibilityLevel(str, enum.Enum):
    SELF = "self"
    TRUSTED = "trusted"
    HEIRS = "heirs"
    PUBLIC = "public"


class SealType(str, enum.Enum):
    NONE = "none"
    UNTIL_DATE = "until_date"
    UNTIL_EVENT = "until_event"
    UNTIL_MANUAL = "until_manual"
