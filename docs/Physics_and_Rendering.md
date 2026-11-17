# Physical models and rendering conventions - v03

All geometry and fields are evaluated from deterministic formulas at 30 fps.
World coordinates are schematic; no metre scale is claimed. Visual time is
slowed and displacement enlarged. The dots in the parcel scene represent
continuum parcels, not a molecular crystal. Pressure-field sample dots remain
fixed and change colour; they are explicitly different from moving parcels.

## Source, parcels and travelling waves

- Source piston visual frequency: 0.2 Hz; plane compression fronts have
  wavelength 1.25 scene units and speed 0.25 units/s. Thus c = f lambda.
  This is an ideal plane-wave illustration, not free-field piston radiation.
- Tracked parcel: xi = 0.7 sin(2 pi t / 5). The cross marks equilibrium.
  A separate blue marker travels at 1.2 units/s, repeating every five seconds
  across a six-unit illustrative window. It marks propagation, not a parcel.
- Longitudinal array: xi(q,t) = 0.09 sin(2 pi 0.4 t - k q), k = 2 pi / 2.5.
  Signed linearised pressure is proportional to -d(xi)/dq = 0.09 k cos(phase).
  c = 1 unit/s. Maximum displayed strain is about 0.226; ordering is preserved.
  Colour uses the linear approximation, not exact nonlinear density.
- Frequency graphs use angular wavenumbers 1.5 and 3, frequencies 0.2 and
  0.4 Hz, so both have the same propagation speed. The amplitude comparison is
  0.45 versus 0.9. Harmonics use integer multiples of both frequency and
  wavenumber. Graph height is not transverse motion of air.

## Diffraction

The outgoing field is a sum of uniformly phased monopole contributions across
a line aperture: F(x,y) = mean(exp(i k r_j) / r_j). A constant global factor
normalises this field; displayed pressure is Re(F exp(-i omega t)).
lambda = 1.5, f = 1/3 Hz, c = 0.5 units/s. Incident fronts use this same
wavelength and speed. Opening widths are 1.4 and 3.4 units, respectively
0.93 and 2.27 wavelengths.

This is a scalar Huygens-style aperture approximation using 3D Green functions
on a line. It is not an exact rigid-wall boundary-value solution, a full
infinite-height slit calculation, or a fluid simulation. It qualitatively
shows interference of aperture contributions and a change of angular spread.
No claim of measured quantitative directivity is made.

## Interference and beats

Two point contributions use exp(i k r)/r, with a near-source cutoff of 0.35
units to avoid the ideal point-source singularity. Equal-frequency views have
lambda=1.8, f=0.4, c=0.72. The opposite-phase view adds pi to one source.
Pressure is summed with its sign; colours do not represent intensity.

The beats view has visual frequencies 2 and 2.2 Hz and common c=3.6 units/s.
Its wavelengths are 1.8 and 3.6/2.2. The beat frequency is 0.2 Hz, so the
envelope repeats in five seconds. These visual parameters are not the audible
400/403 Hz example: audible and slowed visual demonstrations use separate
time scales, not a literal shared carrier phase.

## Standing waves

A rigid-ended column has L=8, k=pi/L, visual f=0.2 Hz:
xi = A sin(k x) cos(omega t), p' = -B A k cos(k x) cos(omega t).
The independently normalised displacement and pressure profiles are plotted
in different rows. Their spatial nodes differ. Both ends are displacement
nodes and pressure antinodes; the pressure node lies at the centre.
Neighbouring displacement nodes are L=lambda/2 apart. Small white parcels
also show longitudinal displacement along the displacement baseline.

## Boundaries, room and hearing

Moving markers illustrate incident, reflected and transmitted pulse paths.
The reflection angle is equal to the incident angle at the plane. Marker
arrival times follow path length at the chosen schematic speed. Marker size
does not encode a calibrated energy fraction. Room paths demonstrate multiple
arrival lengths; they are not a calculated room impulse response. Treated
reflections have reduced marker amplitude, without claiming specific material
absorption coefficients. The hearing view is a functional schematic, not an
anatomically accurate cochlear travelling-wave model.

## Doppler

The source follows x_s(t)=1.3 sin(2 pi t/10). Medium speed c=1.4. Its maximum
speed is 1.3*(2 pi/10)=0.817 < c, so it remains subsonic. Each front has radius
c(t-t_e) and centre x_s(t_e), fixed at emission. Emissions are spaced by 0.5 s.
The display retains five seconds of history. Circles are sections of spherical
fronts. The audible Doppler example uses emission phase at the retarded time,
solving t-t_e=(4-x_s(t_e))/c for a stationary receiver to the right.

## References

- OpenStax, University Physics Volume 1, Sound Waves:
  https://openstax.org/books/university-physics-volume-1/pages/17-1-sound-waves
- Speed of Sound:
  https://openstax.org/books/university-physics-volume-1/pages/17-2-speed-of-sound
- Sound Intensity:
  https://openstax.org/books/university-physics-volume-1/pages/17-3-sound-intensity
- Normal Modes of a Standing Sound Wave:
  https://openstax.org/books/university-physics-volume-1/pages/17-4-normal-modes-of-a-standing-sound-wave
- The Doppler Effect:
  https://openstax.org/books/university-physics-volume-1/pages/17-7-the-doppler-effect
- Single-Slit Diffraction (wave principle):
  https://openstax.org/books/university-physics-volume-3/pages/4-1-single-slit-diffraction
- NIH/NIDCD, How Do We Hear?: https://www.nidcd.nih.gov/health/how-do-we-hear

References checked 2026-11-01. Script and models are original explanatory
implementations based on these principles, not quotations or measured data.
