@login
Feature: Login
  As a Swag Labs customer
  I want to log in with my credentials
  So that I can browse and buy products

  Background:
    Given I am on the login page

  @smoke
  Scenario: Successful login with a standard user
    When I log in as "standard_user" with password "secret_sauce"
    Then I see the products page

  Scenario Outline: Login is rejected for invalid or blocked accounts
    When I log in as "<username>" with password "<password>"
    Then I see the login error "<message>"

    Examples:
      | username        | password     | message                                                                   |
      | locked_out_user | secret_sauce | Epic sadface: Sorry, this user has been locked out.                       |
      | standard_user   | wrong_pass   | Epic sadface: Username and password do not match any user in this service |
