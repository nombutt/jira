# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import getpass
import pytest
# from tenacity import retry
# from tenacity import wait_incrementing
from tests import get_unique_project_name
from tests import JiraTestManager

from jira import Role, Issue, JIRA, JIRAError, Project  # noqa
import jira.client


@pytest.fixture()
def prep():
    pass


@pytest.fixture(scope='module')
def test_manager():
    return JiraTestManager()


@pytest.fixture()
def cl_admin(test_manager):
    return test_manager.jira_admin


@pytest.fixture()
def cl_normal(test_manager):
    return test_manager.jira_normal


@pytest.fixture(scope='function')
def slug(request, cl_admin):
    def remove_by_slug():
        try:
            cl_admin.delete_project(slug)
        except (ValueError, JIRAError):
            # Some tests have project already removed, so we stay silent
            pass

    slug = get_unique_project_name()

    project_name = (
        "Test user=%s key=%s A" % (getpass.getuser(), slug)
    )

    try:
        proj = cl_admin.project(slug)
    except JIRAError:
        proj = cl_admin.create_project(slug, project_name)
    assert proj

    request.addfinalizer(remove_by_slug)

    return slug


def test_delete_project(cl_admin, cl_normal, slug):

    assert cl_admin.delete_project(slug)


def test_delete_inexistent_project(cl_admin):
    slug = 'abogus123'
    with pytest.raises(JIRAError) as ex:
        assert cl_admin.delete_project(slug)

    assert (
        'No project could be found with key' in str(ex.value) or
        'Parameter pid="%s" is not a Project, projectID or slug' % slug in
        str(ex.value)
    )


def test_templates(cl_admin):
    templates = cl_admin.templates()
    expected_templates = set(filter(None, """
Agility
Basic
Bug tracking
Content Management
Customer service
Document Approval
IT Service Desk
Kanban software development
Lead Tracking
Process management
Procurement
Project management
Recruitment
Scrum software development
Task management
""".split('\n')))

    for t in expected_templates:
        assert t in templates


def test_result_list():
    iterable = [2, 3]
    startAt = 0
    maxResults = 50
    total = 2

    results = jira.client.ResultList(iterable, startAt, maxResults, total)

    for idx, result in enumerate(results):
        assert results[idx] == iterable[idx]

    assert next(results) == iterable[0]
    assert next(results) == iterable[1]

    with pytest.raises(StopIteration):
        next(results)


def test_result_list_if_empty():
    results = jira.client.ResultList()

    for r in results:
        raise AssertionError("`results` should be empty")

    with pytest.raises(StopIteration):
        next(results)
