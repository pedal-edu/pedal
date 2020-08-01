
Groups of Feedback

Certainly, you can have more than one group active at a time, right?
    Yes, nested unit tests, unit tests within phases, phases within sections.
    

Can groups contain other groups?
    Are groups themselves Feedback?
        They do have a label vs. human-readable title
        Could have a tool
        Could cross categories and kinds
            Group category? That would seem to make sense.
        Justification is complex
            But good to be explicit in the group's logic about its components.
        Could have their own impact on Score, Correct, Muted, Unscored
    Perhaps instead, we need a "parent" relationship?
        You can have at most one direct parent Feedback (or None)
        Resolvers would typically want to put a parent before its children.

How does a score and correctness work inside of a group?
    Score is a percentage of the current group
        If None, then give them all an equal percentage of the non-explicitly-scored total
    If any element of the group is not correct, then the group is not correct.
        

Groups have
    Name <- Does this uniquely identify them?
    Feedbacks
    
    def new_feedback(self, feedback):
        """ Callback for the report """
    

Use cases:
    Sections of source code
        Section 1, Section 2, Section 3
    Unit Test Group
        "Test add"
        "Test Banana"
    Phases of checks
        "Phase 1"

Groups can be correct or incorrect, can't they?
    Section one is correct
        So is set_success local to the current group?
        Maybe not by default:
            set_success(group='Test add')

Sections can be created and accessed the same way:
    As in `section(1)`
    The reason is because you can then create them as needed, lazily.

Do Groups get their own resolvers?
    In a way, their behavior is like a Mini-Resolver.
    Should there be mechanisms to override these?
        Phases: 
        Sections: 
        Test Groups: 

Phases can be within sections
    So how do you avoid phases in part 2 affecting part 3?
        Phases must be group local.
Can you have sections within phases
    No, that could potentially require multiple sectionings in a single file, which is not possible (and too complicated).


I create these phases
    Phase 1
    Phase 2, precondition 1
    Phase 3, precondition 2


If Sources is responsible for Sections
And Assertions is responsible for TestGroups
Who is responsible for Phases?
    Might be Assertions, you typically want to organize them at that level.

How does feedback end up in a Group?
    The Report has a sense of the "current active" Group
        This must be a stack, so when groups begin and end they notify the Report
    The Report checks in with the current Group about whether they want the given piece of feedback.

Is there a global Group?
    This would simplify code to avoid None checks.
    Nah, that's just going to lead to infinite loops.
