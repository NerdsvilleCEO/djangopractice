import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from firstapp.models import Question

class QuestionClassTests(TestCase):
  def test_was_published_recently_with_future_question(self):
    """
    Should return false if pub_date is in future
    """
    future_date = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=future_date)
    self.assertEqual(future_question.was_published_recently(), False)

  def test_was_published_recently_with_past_question_within_one_day(self):
    """
    Should return true if pub_date is within one day
    """
    past_date = timezone.now() - datetime.timedelta(hours=1)
    past_question = Question(pub_date=past_date)
    self.assertEqual(past_question.was_published_recently(), True)
 
  def test_was_published_recently_with_past_question_past_one_day(self):
    """
    Should return false if pub_date is not within one day
    """
    past_date = timezone.now() - datetime.timedelta(days=2)
    past_question = Question(pub_date=past_date)
    self.assertEqual(past_question.was_published_recently(), False)
 

def create_question(question_text, days):
  time = timezone.now() + datetime.timedelta(days=days)
  return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionViewTests(TestCase):
  def test_index_view_with_no_questions(self):
    """
    If no questions exist, an appropriate message should display
    """
    response = self.client.get(reverse("polls:index"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "No polls are available.")
    self.assertQuerysetEqual(response.context['latest_question_list'], [])
  def test_index_view_with_a_past_question(self):
    """
    Make sure the past question shows up in view on index page
    """
    create_question(question_text="Past Question", days=-30)
    response = self.client.get(reverse("polls:index"))
    self.assertQuerysetEqual(response.context['latest_question_list'], 
                                              ['<Question: Past Question>']
                             )
  
  def test_index_view_with_a_future_question(self):
    """
    Make sure the future question does not show on index page
    """
    create_question(question_text="This will not show", days=300)
    response = self.client.get(reverse("polls:index"))
    self.assertContains(response, "No polls are available")
    self.assertQuerysetEqual(response.context['latest_question_list'],
                                             []
                            )
 
  def test_index_view_with_future_and_past_question(self):
    """
    Make sure only the past question shows up on index page
    """
    create_question(question_text="This will show", days=-30)
    create_question(question_text="This will not show", days=300)
    response = self.client.get(reverse("polls:index"))
    self.assertEqual(response.status_code, 200)
    self.assertQuerysetEqual(response.context['latest_question_list'],
                                             ['<Question: This will show>']
                             )
  def test_index_view_with_two_past_questions(self):
    """
    Should show all past questions
    """
    create_question(question_text="This will show", days=-30)
    create_question(question_text="This will also show", days=-31)
    response = self.client.get(reverse("polls:index"))
    self.assertEqual(response.status_code, 200)
    self.assertQuerysetEqual(response.context['latest_question_list'],
                                              ['<Question: This will show>',
                                               '<Question: This will also show>']

                              )

class QuestionIndexDetailTests(TestCase):
  def test_detail_view_with_future_question(self):
    """
    Should not show up on the view and return a 404
    """
    future_question = create_question(question_text="Futuredated question", 
                                      days=1)
    response = self.client.get(reverse("polls:detail", 
                                       args=(future_question.id,)))
    self.assertEqual(response.status_code, 404)
  
  def test_detail_view_with_past_question(self):
    """
    Should return a 200
    """
    past_question = create_question(question_text="Pastdated question",
                                    days=-1)
    response = self.client.get(reverse("polls:detail",
                                       args=(past_question.id,)))
    self.assertContains(response, past_question.question_text, status_code=200)
