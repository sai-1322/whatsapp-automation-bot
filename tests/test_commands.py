from bot.commands import HELP_TEXT, handle_command


class FakeScheduler:
    def __init__(self):
        self.calls = []

    def __call__(self, sender, minutes, text):
        self.calls.append((sender, minutes, text))


def test_help():
    assert handle_command("help", "1", FakeScheduler()) == HELP_TEXT


def test_greeting_is_case_insensitive():
    assert handle_command("HeLLo", "1", FakeScheduler()) == HELP_TEXT


def test_ping():
    assert handle_command("ping", "1", FakeScheduler()) == "pong"


def test_echo():
    assert handle_command("echo good morning", "1", FakeScheduler()) == "good morning"


def test_echo_without_text():
    assert "Usage" in handle_command("echo", "1", FakeScheduler())


def test_unknown_command():
    assert "didn't understand" in handle_command("dance", "1", FakeScheduler())


def test_empty_message():
    assert "help" in handle_command("   ", "1", FakeScheduler())


def test_remind_schedules_and_confirms():
    sched = FakeScheduler()
    reply = handle_command("remind 10 drink water", "9198", sched)
    assert sched.calls == [("9198", 10.0, "drink water")]
    assert "drink water" in reply


def test_remind_rejects_bad_minutes():
    sched = FakeScheduler()
    assert "Usage" in handle_command("remind abc do it", "1", sched)
    assert sched.calls == []


def test_remind_rejects_missing_text():
    sched = FakeScheduler()
    assert "Usage" in handle_command("remind 5", "1", sched)
    assert sched.calls == []


def test_remind_rejects_out_of_range():
    sched = FakeScheduler()
    assert "between" in handle_command("remind 0 x", "1", sched)
    assert "between" in handle_command("remind 999999 x", "1", sched)
    assert sched.calls == []
