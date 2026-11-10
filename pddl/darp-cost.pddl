(define (domain darp-cost)
  (:requirements :strips :typing :action-costs)
  (:types vehicle passenger location seat)

  (:predicates
    (at-vehicle ?v - vehicle ?l - location)
    (at-passenger ?p - passenger ?l - location)
    (origin ?p - passenger ?l - location)
    (destination ?p - passenger ?l - location)
    (onboard ?p - passenger ?v - vehicle)
    (served ?p - passenger)
    (slot-of ?s - seat ?v - vehicle)
    (free ?s - seat)
    (uses-slot ?p - passenger ?s - seat)
    (connected ?from - location ?to - location)
  )

  (:functions
    (total-cost)
    (travel-cost ?from - location ?to - location)
  )

  (:action drive
    :parameters (?v - vehicle ?from - location ?to - location)
    :precondition (and (at-vehicle ?v ?from) (connected ?from ?to))
    :effect (and
      (not (at-vehicle ?v ?from))
      (at-vehicle ?v ?to)
      (increase (total-cost) (travel-cost ?from ?to))
    )
  )

  (:action pickup
    :parameters (?p - passenger ?v - vehicle ?l - location ?s - seat)
    :precondition (and
      (at-passenger ?p ?l)
      (origin ?p ?l)
      (at-vehicle ?v ?l)
      (slot-of ?s ?v)
      (free ?s)
    )
    :effect (and
      (not (at-passenger ?p ?l))
      (onboard ?p ?v)
      (uses-slot ?p ?s)
      (not (free ?s))
    )
  )

  (:action dropoff
    :parameters (?p - passenger ?v - vehicle ?l - location ?s - seat)
    :precondition (and
      (onboard ?p ?v)
      (destination ?p ?l)
      (at-vehicle ?v ?l)
      (uses-slot ?p ?s)
      (slot-of ?s ?v)
    )
    :effect (and
      (not (onboard ?p ?v))
      (not (uses-slot ?p ?s))
      (free ?s)
      (served ?p)
    )
  )
)
