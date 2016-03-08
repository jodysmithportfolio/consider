"""
section.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor control of adding/removing sections.

- Author(s): Rohit Kapoor, Swaroop Joshi, Tyler Rasor
- Last Modified: March 07, 2016

--------------------


"""
import json

import webapp2
from google.appengine.api import users

from src import models
from src import utils


class Sections(webapp2.RequestHandler):
    """
    Handles requests for managing sections: adding a section, toggling its status, etc.
    """

    def add_section(self, course, section_name):
        """
        Adds a section to the given course in the datastore.

        Args:
            course (object):
                Course to which the section is to be added.
            section_name (str):
                Name of the section; must be unique within the course.

        """
        # First, start by grabbing the section passed in from the database
        section = models.Section.get_by_id(section_name, parent=course.key)
        # Double check that it doesn't already exist
        if section:
            # And send an error if it does
            utils.error(section_name + ' already exists', handler=self)
        else:
            # Otherwise, create it, save it to the database, and log it
            section = models.Section(parent=course.key, id=section_name)
            section.name = section_name
            section.put()
            utils.log(section_name + ' added', type='S')
        #end
    #end add_section

    def toggle_section(self, course, section_name):
        """
        Toggles the status of a section between Active and Inactive.

        Args:
            course (object):
                Course under which this section exists
            section_name (str):
                Name of the section to be toggled.

        """
        # First, start by grabbing the section from the passed in value
        section = models.Section.get_by_id(section_name, parent=course.key)
        # Double check that it actually exists
        if section:
            # Toggle the section to active, save it to the database, and log it
            section.is_active = not section.is_active
            section.put()
            utils.log('Status changed for ' + section_name, type='S')
        else:
            # Send an error if the section passed in doesn't exist
            utils.error('Section ' + section_name + ' not found', handler=self)
        #end
    #end toggle_section

    def post(self):
        """
        HTTP POST method to add a section to a course.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(models.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        #end

        # Otherwise, grab the course, section, and action from the webpage
        course_name = self.request.get('course')
        section_name = self.request.get('section')
        action = self.request.get('action')
        # Double check that all three were supplied
        if not course_name or not section_name or not action:
            # Error if not
            utils.error('Invalid arguments: course_name or section_name or action is null', handler=self)
        else:
            # Otherwise, grab the course from the database
            course = models.Course.get_by_id(course_name.upper(), parent=instructor.key)
            # And check that it exists and is active
            if not course or not course.is_active:
                # Error if not
                utils.error(course_name + ' does not exist OR is not active!', handler=self)
            else:
                # Otherwise, switch on the action
                if action == 'add':
                    # Add a new section if action is add
                    self.add_section(course, section_name.upper())
                elif action == 'toggle':
                    # Or toggle
                    self.toggle_section(course, section_name.upper())
                else:
                    # Error if the action is neither toggle or add
                    utils.error('Unexpected action:' + action, handler=self)
                #end
            #end
        #end
    #end post

    def get(self):
        self.redirect('/courses')
    #end get

#end class Section
