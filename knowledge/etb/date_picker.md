# ETB Date Picker Directive

Status: APPROVED ENGINEERING DIRECTIVE
Priority: English ETB delivery

When ETB reaches date-picker implementation, the runtime-proven NTB date-picker
implementation is the canonical reference.

ETB must reuse the NTB implementation's:

- interaction strategy;
- synchronization strategy;
- scroll behavior;
- retry behavior.

Preserve existing NTB behavior. Do not maintain a parallel ETB-specific date
picker unless fresh runtime evidence proves that ETB cannot use the NTB
implementation. Any divergence requires a bounded evidence record identifying
the incompatible behavior and an explicit Hermes engineering decision.

Thai ETB support is out of scope until English ETB delivery is ready.
