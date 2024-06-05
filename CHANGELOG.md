# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.3.4 [2021-09-13]

### Added

- New time windows restriction in RoutingScheduler for fulfill order's interval

### Changed

- Update OR-tools version from v7.2 to v8.0

### Fixed

- Potencial bug in OR-tools solvers in proto-variables is already solved

### Removed

## 0.3.3 [2021-08-26]

### Added

### Changed

- Numpy updated from 1.19 to 1.20
- Update encouraged when working with Behaviour Prediction and Anomaly Detection

### Fixed

### Removed

## 0.3.2 [2021-06-23]

### Added

- JustInTime algorithm was included into the Inventory algorithms.
- Complete behavioral tests to checks ignitions and order placer in FlowShop algorithm.
- New constrain of user's stops in Routing Scheduler through the method ´add_stops´ and ´or_result´.

### Changed

### Fixed

### Removed

## 0.3.1 [2021-06-25]

### Added

- Fixers, Flowshop and RoutingScheduler now consider adding the recipe in plan instace output

### Changed

- Schedule-Logic version update from v1.1.4 to v1.1.5

### Fixed

### Removed

## 0.3.0 [2021-06-25]

### Added

- New RoutingScheduler planner included into the scheduling models
- New Fixers models to repair messed production program
  - Graph recipe dependeny no-overlap fixer in `solve_overlaped_dependency`
  - Resource no-overlap fixer in `solve_overlaped_plans`
  - Fastforwarding fixer in plans by default enabled
  - Backforwarding fixer in plans by default enabled

### Changed

### Fixed

### Removed

## 0.2.2 [2021-07-21]

### Added

### Changed

- Validator of Orders now must validate 'name' instead of 'code'

### Fixed

### Removed

## 0.2.1 [2021-04-16]

### Added

- Flowshop now is able to consider prior stops into planning
- Flowshop now can link python functions with Schedule-Logic's Function
- New model generators:
  - build_demand
  - build_uoms
  - build_functions
  - build_stops
- New validators:
  - valid_plan
  - valid_stop

### Changed

- Schedule-Logic updated to v1.1.1
- PriorityScheduler refactored. Now can be accessed easily with self-explained methods
- The way recipes are set into Flowshop was changed. Now it only accept list instead of sigle instances

### Fixed

- Bug setting environment 'test'. Now user only can set 'dev' or 'prod' environments

### Removed

## 0.2.0 [2021-03-22]

### Added

### Changed

- PriorityScheduler now can calculate weighted priority by any user input

### Fixed

- Now module can be imported inside another ones with `import scheduler`.

### Removed

- scikit-learn (v0.24.1) was dismissed

## 0.1.0 [2021-03-19]

### Added

- New PriorityScheduler algorithm
- New data validators created for the following models:
  - demand
  - order
  - lot
  - inventoryGroup
  - program
  - plans
  - material
  - resource
  - process
  - recipe
  - function
  - metadata
- These validators run as a firewall to prevent the user from entering inconsistent data in the flowshop and priorityscheduler algorithms.
- Transition restrictions between processes can now be implemented by the user
- New method set_scale to specify the degree of precision in flowshop
- Automatic data constructors for the execution of random cases
  - materials
  - means
  - recipes
- New helper functions in datetools:
  - round_date
  - is_intersected

### Changed

Gantts generator display improvement

- new labels
- automatic text fitting to plans

### Fixed

- Rounding errors in the scale were corrected in the flowshop tests.
- Bug in wrong copy of recipe templates fixed

### Removed

## 0.0.2 [2021-02-16]

### Added

- Flowshop solver tested and ready to be used compatible with Schedule-Logic v1.0.4
- The Flowshop's engine added the following constraints:
  - add_dependency
  - add_resource_no_overlap (optional: transitions)
  - add_optional_process
  - add_single_recipe
- New build-in optimization function for Flowshop:
  - makespan
  - transitions
- New modes to add a new recipe to scheduler
  - default: all process from a same recipe are scheduled
  - batch: processes with dependency link and same resource are locked
- New method capable of traducing OR-tools variables into a Schedule-Logic's Program
- Distribution generator added with the following functions:
  - betavariate
  - choice
  - choices
  - expovariate
  - gammavariate
  - gauss
  - getrandbits
  - getstate
  - lognormvariate
  - normalvariate
  - paretovariate
  - randint
  - random
  - randrange
  - sample
  - setstate
  - shuffle
  - triangular
  - uniform
  - vonmisesvariate
  - weibullvariate
  - uuid1 (random string)
  - uuid4 (random string)
- Graph generator added to make random graphs of the following types:
  - tree (Non-binary Tree)
  - dag (Directed Acyclic Graph)
  - rootdag (Rooted Directed Acyclic Graph)
  - path (Directed Path Graph)
- Model generator added to make Schedule-Logic's objects with valid fictional data (using both distribution and graph generators). Some functionalities include:
  - build fictional manufacturing plant connected as a random graph
  - build fictional materials (products and materials)
  - build fictional recipes appending to products as a random dag graph
  - build fictional stops for simulating maintanance in scheduler
  - build fictional demand for simulating valid inputs in scheduler
  - build single Schedule-Logic's model
- New function to plot a Gantt given a valid Program using matplotlib
- New function to plot a network dependency graph given a valid Recipe
- Context manager added to print concise and useful information when any scheduler's algorithm is running
- Report function added in order to give some general stats like runtime when any scheduler's algorithm ends

## Changed

- Schedule-Logic version changed to v1.0.4

## 0.0.1-b [2020-11-17]

### Added

- More test documentation added to [Resources](https://drive.google.com/drive/folders/17iTPJsiMs3B1UXlq-4gJzJVMntxDx9k1)
- New behavioral unproved tests to FlowShop algorithm (currently on development)
- New helper utility for datetime transfomation to integers
- New tests that proved and ensure funcionality of previous utility

## Changed

- Defined pytest version to 6.1
- Defined pytest-cov version to 2.10
- Defined pylint version to 2.6
- Defined sphinx version to 3.1
- Defined sphinx-rtd-theme version to 0.5.0
- Defined autopep8 version to 1.5
- Defined gstorm version to 0.5
- Defined redis version to 3.5
- Defined ortools version to 7.8
- Defined numpy version to 1.19

## 0.0.1 [2020-11-05]

### Added

- README with basic setup
- Pull Request template
- This CHANGELOG
- Project structure
- Setup files
- PYPI config
- Sphinx Autodomentation
- Auto-testing workflow
- Pytest files
