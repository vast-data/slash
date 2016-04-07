import pytest
import slash
from slash.loader import Loader

from .utils import make_runnable_tests


def test_requirements_mismatch_session_success(suite, suite_test):
    suite_test.add_decorator('slash.requires(False)')
    suite_test.expect_skip()
    summary = suite.run()
    assert summary.session.results.is_success(allow_skips=True)


@pytest.mark.parametrize('requirement_fullfilled', [True, False])
@pytest.mark.parametrize('use_message', [True, False])
@pytest.mark.parametrize('use_fixtures', [True, False])
@pytest.mark.parametrize('message_in_retval', [True, False])
def test_requirements(suite, suite_test, requirement_fullfilled, use_fixtures, use_message, message_in_retval):

    message = "requires something very important"
    if use_message and message_in_retval:
        retval = '({}, {!r})'.format(requirement_fullfilled, message)
    else:
        retval = requirement_fullfilled

    suite_test.add_decorator('slash.requires((lambda: {0}), {1!r})'.format(retval, message if use_message and not message_in_retval else ''))
    if not requirement_fullfilled:
        suite_test.expect_skip()

    if use_fixtures:
        suite_test.depend_on_fixture(
            suite.slashconf.add_fixture())
    results = suite.run()
    if requirement_fullfilled:
        assert results[suite_test].is_success()
    else:
        assert not results[suite_test].is_started()
        assert results[suite_test].is_skip()
        if use_message:
            [skip] = results[suite_test].get_skips()
            assert message in skip


def test_requirements_on_class():

    def req1():
        pass

    def req2():
        pass

    @slash.requires(req1)
    class Test(slash.Test):

        @slash.requires(req2)
        def test_something(self):
            pass

    with slash.Session():
        [test] = make_runnable_tests(Test)

    assert [r._req for r in test.get_requirements()] == [req1, req2]
