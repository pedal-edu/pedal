# Questions Tool

The questions model flips the script of Feedback generation to also generate
instructions. It is assumed that an environment would provide some initial
meta-instruction, and that initial evaluation would generate some new question
specific instructions.

Taxonomy:
* Question: A bundle of instructions and tests that can be delivered to a
            student, not as feedback, but as a narrowing/modification of the
            original problem.
* Pool: A collection of Questions that can be drawn from randomly to
        individualize the student experiment.
* Instructions: The (HTML) text rendered to the learner to prepare them for
         a question. The default is to assume that this would be static,
         but more interesting possibilities could occur.
* Tests: The collection of feedback control logic that is bundled for this
         question. This speaks to the idea of better encapsulation for
         the control logic - perhaps it is time for the Organizers from
         Assertions to be promoted to their own Tool?
* Seed: A value (expected to be constant for a given user) that can act as
        an "offset" for selecting problems. This allows users to
        deterministically receive feedback from a feedback engine.
        Numeric seeds allow specifically selecting questions from the pool,
        while String seeds are hashed to "random" indexes. An example is to
        use student usernames, emails, or internal IDs (probably better to
        treat numeric IDs as strings).
        
# Delivery

By default, new question text is delivered by the Resolver as feedback
that appears at the top of all the other feedback without preventing any
subsequent feedback, similar to the way Compliments do not prevent actual
feedback.

However, Resolvers probably want to override this. For example, BlockPy would
probably want to modify the problem instructions area. VPL would probably
want to isolate the instructions to their own group or to provide a header with
them.
        
# Timing

Here are a few different models of the timing of questions:
1. The student requests initial feedback, and all questions appear.
2. The student indicates in some way which question they want to appear,
   and that question's Instructions appear.
3. Students are given a single initial question, and when they complete it,
   the text of a new question appears.
4. Instead of a single question appearing, the students are presented with
   a choice of questions (see CYOA).

# Random Pool

Frequently, instructors need to be able to draw a question from a pool.

A design principle based on research is that questions should be as equal
in difficulty and learning objectives as possible. Granted - there are
pedagogical design decisions that could justify breaking that guideline.
We should encourage question equivalency but allow the instructor to have
wildly different questions.

In theory, question selection doesn't have to be random. Subclasses
could be created that draw on data sources about the user - these could
be local data sources ("You struggled a lot on the last question, so let's
try another one that's similar") or more exotic ("My records indicate that you
haven't really mastered IF statements, so let's do some practice with that.")

# Templated Questions

Being able to generate questions based on a template or some rules appears
to be a popular request. In the Random Pool model, we had a static set of
Questions. But now we have a series of rules for generating questions.

TemplateQuestion is a class for creating questions from finite sets of terms.
You provide a set of variables, some templated text (Python Format? Jinja2?),
and the set of values for variables. From this, questions could be automatically
generated.

DynamicQuestion is a more general-purpose class for true dynamic generation of
problems. The model here would be to subclass and redefine components
by overriding methods.

# CYOA

One of the more interesting ideas is to support Choose-Your-Own-Adventure
style chains of questions. In this model, completing a question could unlock
multiple paths to move forward on.

Open Questions:
* How do students indicate a choice along the path?
* How do we elegantly connect Decision A with Paths B, C, and D; keeping
  in mind that game flow is a DAG or possibly even a graph.
