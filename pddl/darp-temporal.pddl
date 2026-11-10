(define (domain darp-temporal)
  (:requirements :typing :durative-actions :fluents :timed-initial-literals)
  (:types vehicle passenger location)

  (:predicates
    (at-vehicle ?v - vehicle ?l - location)
    (waiting ?p - passenger ?l - location)
    (destination ?p - passenger ?l - location)
    (ready ?p - passenger)
    (available ?v - vehicle)
    (onboard ?p - passenger ?v - vehicle)
    (served ?p - passenger)
    (connected ?from - location ?to - location)
  )

  (:functions
    (travel-time ?from - location ?to - location)
    (load ?v - vehicle)
    (capacity ?v - vehicle)
    (total-travel)
  )

  (:durative-action drive
    :parameters (?v - vehicle ?from - location ?to - location)
    :duration (= ?duration (travel-time ?from ?to))
    :condition (and
      (at start (available ?v))
      (at start (at-vehicle ?v ?from))
      (at start (connected ?from ?to))
    )
    :effect (and
      (at start (not (available ?v)))
      (at start (not (at-vehicle ?v ?from)))
      (at end (at-vehicle ?v ?to))
      (at end (available ?v))
      (at end (increase (total-travel) (travel-time ?from ?to)))
    )
  )

  (:durative-action pickup
    :parameters (?p - passenger ?v - vehicle ?l - location)
    :duration (= ?duration 1)
    :condition (and
      (at start (available ?v))
      (at start (waiting ?p ?l))
      (at start (ready ?p))
      (at start (at-vehicle ?v ?l))
      (at start (< (load ?v) (capacity ?v)))
    )
    :effect (and
      (at start (not (available ?v)))
      (at start (not (waiting ?p ?l)))
      (at end (onboard ?p ?v))
      (at end (increase (load ?v) 1))
      (at end (available ?v))
    )
  )

  (:durative-action dropoff
    :parameters (?p - passenger ?v - vehicle ?l - location)
    :duration (= ?duration 1)
    :condition (and
      (at start (available ?v))
      (at start (onboard ?p ?v))
      (at start (destination ?p ?l))
      (at start (at-vehicle ?v ?l))
    )
    :effect (and
      (at start (not (available ?v)))
      (at start (not (onboard ?p ?v)))
      (at end (served ?p))
      (at end (decrease (load ?v) 1))
      (at end (available ?v))
    )
  )
)
