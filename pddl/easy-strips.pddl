(define (problem darp-easy-strips)
  (:domain darp-strips)
  (:objects
    v1 - vehicle
    p1 - passenger
    l0 l1 l2 - location
    s1_1 - seat
  )
  (:init
    (at-vehicle v1 l0)
    (at-passenger p1 l1)
    (origin p1 l1)
    (destination p1 l2)
    (slot-of s1_1 v1)
    (free s1_1)
    (connected l0 l1)
    (connected l0 l2)
    (connected l1 l0)
    (connected l1 l2)
    (connected l2 l0)
    (connected l2 l1)
  )
  (:goal (and (served p1)))
)
