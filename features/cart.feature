@cart
Feature: Shopping cart
  As a logged-in customer
  I want to add products to my cart
  So that I can buy them later

  Background:
    Given I am logged in as "standard_user"

  @smoke
  Scenario: Add a single product to the cart
    When I add "Sauce Labs Backpack" to the cart
    Then the cart badge shows 1
    When I open the cart
    Then the cart contains "Sauce Labs Backpack"

  Scenario: Add several products to the cart
    When I add "Sauce Labs Backpack" to the cart
    And I add "Sauce Labs Bike Light" to the cart
    Then the cart badge shows 2
