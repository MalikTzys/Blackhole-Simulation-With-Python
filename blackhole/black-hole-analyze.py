import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D
import time

# Konstanta fisika
G = 6.67430e-11
c = 299792458
M_sun = 1.989e30

class BlackHoleSimulator:
    def __init__(self, mass=15, n_particles=5000, n_photons=1000, n_jets=300):
        """Simulasi Black Hole CPU Optimized"""
        print("Inisialisasi Black Hole Simulator...")
        
        self.M = mass * M_sun
        self.rs = 2 * G * self.M / (c**2)
        self.n_particles = n_particles
        self.n_photons = n_photons
        self.n_jets = n_jets
        self.time = 0
        
        print(f"✓ Schwarzschild Radius: {self.rs:.2e} m")
        print(f"✓ Massa: {mass} M☉")
        
        self._init_particles()
        self._init_photons()
        self._init_jets()
        self._init_stars()
        
        print(f"✓ {n_particles} partikel disk")
        print(f"✓ {n_photons} photons")
        print(f"✓ {n_jets} partikel jets")
        print(f"✓ Background stars")
        
    def _init_particles(self):
        """Inisialisasi accretion disk - Interstellar Gargantua style"""
        # Radius dengan power law - disk lebih tebal di tengah
        r_uniform = np.random.random(self.n_particles)
        r = 3*self.rs + np.power(r_uniform, 0.6) * 17*self.rs
        
        # Sudut dengan spiral pattern yang lebih pronounced
        theta = np.random.uniform(0, 2*np.pi, self.n_particles)
        spiral = np.log(r / (3*self.rs)) * 0.4
        theta += spiral
        
        # Posisi 3D - disk lebih tipis seperti di Interstellar
        self.x = r * np.cos(theta)
        self.y = r * np.sin(theta)
        self.z = np.random.normal(0, 0.08*r/self.rs, self.n_particles)
        
        # Kecepatan orbital Keplerian
        v_orbital = np.sqrt(G * self.M / r)
        turb = np.random.normal(0, 0.06*v_orbital, self.n_particles)
        
        self.vx = -v_orbital * np.sin(theta) + turb
        self.vy = v_orbital * np.cos(theta) + turb
        self.vz = np.random.normal(0, 0.008*v_orbital, self.n_particles)
        
        # Temperature untuk visualisasi
        self.update_temperature()
        
    def _init_photons(self):
        """Inisialisasi photons untuk lensing"""
        self.px = np.random.uniform(-35*self.rs, 35*self.rs, self.n_photons).astype(np.float64)
        self.py = np.full(self.n_photons, -60*self.rs, dtype=np.float64)
        self.pvx = np.zeros(self.n_photons, dtype=np.float64)
        self.pvy = np.full(self.n_photons, c, dtype=np.float64)
        
    def _init_jets(self):
        """Inisialisasi relativistic jets"""
        # Jets dari poles
        r_jet = np.random.uniform(0, 0.8*self.rs, self.n_jets)
        theta_jet = np.random.uniform(0, 2*np.pi, self.n_jets)
        z_start = np.random.uniform(1*self.rs, 3*self.rs, self.n_jets)
        
        self.jx = r_jet * np.cos(theta_jet)
        self.jy = r_jet * np.sin(theta_jet)
        self.jz = z_start * np.random.choice([-1, 1], self.n_jets)
        
        # Kecepatan relativistik
        v_jet = 0.95 * c
        self.jvx = np.random.normal(0, 0.05*v_jet, self.n_jets)
        self.jvy = np.random.normal(0, 0.05*v_jet, self.n_jets)
        self.jvz = np.sign(self.jz) * v_jet
        
        self.jet_energy = np.ones(self.n_jets)
        
    def _init_stars(self):
        """Background stars"""
        self.n_stars = 150
        self.sx = np.random.uniform(-45*self.rs, 45*self.rs, self.n_stars)
        self.sy = np.random.uniform(-45*self.rs, 45*self.rs, self.n_stars)
        self.s_brightness = np.random.uniform(0.4, 1.0, self.n_stars)
        
    def update_temperature(self):
        """Update temperature berdasarkan posisi - Interstellar style"""
        r = np.sqrt(self.x**2 + self.y**2 + self.z**2)
        r_safe = np.maximum(r, 0.1*self.rs)
        
        # Temperature profile seperti Gargantua (kuning-oranye)
        # Inner region lebih panas (putih-kuning), outer cooler (oranye-merah)
        self.temperature = np.power(self.rs / r_safe, 0.7) * 1.8  # Boost brightness
        self.temperature = np.minimum(self.temperature, 3.5)
        
        # Tambah variasi untuk flicker effect
        self.temperature += np.random.normal(0, 0.08, self.n_particles)
        self.temperature = np.maximum(self.temperature, 0.6)  # Minimum brightness lebih tinggi
        
    def update_particles(self, dt):
        """Update partikel disk"""
        # Jarak dari pusat
        r = np.sqrt(self.x**2 + self.y**2 + self.z**2)
        r_safe = np.maximum(r, 0.1*self.rs)
        
        # Gravitasi dengan koreksi relativistik
        a_mag = -G * self.M / (r_safe**2)
        correction = 1.0 + 3.0*(self.rs/r_safe) + 2.0*(self.rs/r_safe)**2
        a_mag *= correction
        
        # Komponen akselerasi
        ax = a_mag * self.x / r_safe
        ay = a_mag * self.y / r_safe
        az = a_mag * self.z / r_safe
        
        # Radiation pressure dari inner disk
        radiation = np.exp(-r_safe / (3*self.rs)) * 0.02 * c
        ax += radiation * self.x / r_safe
        ay += radiation * self.y / r_safe
        az += radiation * self.z / r_safe
        
        # Frame-dragging (rotasi ruang-waktu)
        omega = np.sqrt(G * self.M / r_safe**3) * 0.15
        ax -= omega * self.y
        ay += omega * self.x
        
        # Update kecepatan
        self.vx += ax * dt
        self.vy += ay * dt
        self.vz += az * dt
        
        # Viscosity (drag)
        drag = 0.998
        self.vx *= drag
        self.vy *= drag
        self.vz *= drag * drag  # Lebih kuat di z
        
        # Update posisi
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        
        # Respawn partikel yang jatuh
        fallen = r < 1.5 * self.rs
        n_respawn = np.sum(fallen)
        
        if n_respawn > 0:
            r_new = np.random.uniform(15*self.rs, 20*self.rs, n_respawn)
            theta_new = np.random.uniform(0, 2*np.pi, n_respawn)
            
            self.x[fallen] = r_new * np.cos(theta_new)
            self.y[fallen] = r_new * np.sin(theta_new)
            self.z[fallen] = np.random.normal(0, 0.1*self.rs, n_respawn)
            
            v_new = np.sqrt(G * self.M / r_new)
            self.vx[fallen] = -v_new * np.sin(theta_new)
            self.vy[fallen] = v_new * np.cos(theta_new)
            self.vz[fallen] = 0
            
        # Update temperature
        self.update_temperature()
        
    def update_photons(self, dt):
        """Update photon trajectories dengan lensing"""
        # Jarak dari black hole
        r = np.sqrt(self.px**2 + self.py**2)
        r_safe = np.maximum(r, 0.5*self.rs)
        
        # Defleksi gravitasi
        deflection = 4 * G * self.M / (c**2 * r_safe)
        deflection *= (1.0 + 15*(self.rs/r_safe)/4)  # Post-Newtonian
        
        # Update kecepatan photon
        self.pvx += -deflection * self.px / r_safe * c * dt
        self.pvy += -deflection * self.py / r_safe * c * dt
        
        # Normalisasi ke kecepatan cahaya
        v_mag = np.sqrt(self.pvx**2 + self.pvy**2)
        v_mag = np.maximum(v_mag, 1e-10)
        self.pvx = self.pvx / v_mag * c
        self.pvy = self.pvy / v_mag * c
        
        # Update posisi
        self.px += self.pvx * dt
        self.py += self.pvy * dt
        
        # Respawn photon yang keluar atau masuk
        escaped = (self.py > 60*self.rs) | (r < 1.5*self.rs) | (np.abs(self.px) > 40*self.rs)
        n_respawn = np.sum(escaped)
        
        if n_respawn > 0:
            self.px[escaped] = np.random.uniform(-35*self.rs, 35*self.rs, n_respawn)
            self.py[escaped] = -60 * self.rs
            self.pvx[escaped] = 0
            self.pvy[escaped] = c
            
    def update_jets(self, dt):
        """Update jets"""
        # Update posisi
        self.jx += self.jvx * dt
        self.jy += self.jvy * dt
        self.jz += self.jvz * dt
        
        # Energy decay
        self.jet_energy *= 0.995
        
        # Respawn jets
        far = (np.abs(self.jz) > 45*self.rs) | (self.jet_energy < 0.15)
        n_respawn = np.sum(far)
        
        if n_respawn > 0:
            r_new = np.random.uniform(0, 0.8*self.rs, n_respawn)
            theta_new = np.random.uniform(0, 2*np.pi, n_respawn)
            z_new = np.random.uniform(1*self.rs, 3*self.rs, n_respawn)
            
            self.jx[far] = r_new * np.cos(theta_new)
            self.jy[far] = r_new * np.sin(theta_new)
            self.jz[far] = z_new * np.random.choice([-1, 1], n_respawn)
            
            v_jet = 0.95 * c
            self.jvx[far] = np.random.normal(0, 0.05*v_jet, n_respawn)
            self.jvy[far] = np.random.normal(0, 0.05*v_jet, n_respawn)
            self.jvz[far] = np.sign(self.jz[far]) * v_jet
            self.jet_energy[far] = 1.0
            
    def update(self, dt):
        """Update semua komponen"""
        self.update_particles(dt)
        self.update_photons(dt)
        self.update_jets(dt)
        self.time += dt

# Inisialisasi
print("=" * 65)
print("   🌌 GARGANTUA - INTERSTELLAR BLACK HOLE")
print("=" * 65)
print("\nFitur:")
print("  ✓ Accretion Disk kuning-oranye (seperti Gargantua)")
print("  ✓ Relativistic Jets biru")
print("  ✓ Gravitational Lensing")
print("  ✓ Post-Newtonian physics")
print("  ✓ Frame-dragging effect")
print("  ✓ Radiation pressure")
print()

bh = BlackHoleSimulator(mass=15, n_particles=5000, n_photons=1000, n_jets=300)

print("\n✓ Semua sistem siap!")
print("=" * 65)

# Visualisasi
fig = plt.figure(figsize=(20, 7), facecolor='#000814')
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

# Panel 1: Top View
ax1 = fig.add_subplot(gs[:, 0])
ax1.set_xlim(-25, 25)
ax1.set_ylim(-25, 25)
ax1.set_aspect('equal')
ax1.set_facecolor('#000814')
ax1.set_title('Top View - Accretion Disk', color='#00d9ff', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('X (Schwarzschild radii)', color='#00d9ff', fontsize=10)
ax1.set_ylabel('Y (Schwarzschild radii)', color='#00d9ff', fontsize=10)
ax1.tick_params(colors='#00d9ff', labelsize=8)
ax1.grid(True, alpha=0.15, color='#00d9ff', linestyle=':')

# Panel 2: Side View
ax2 = fig.add_subplot(gs[:, 1])
ax2.set_xlim(-40, 40)
ax2.set_ylim(-65, 65)
ax2.set_aspect('equal')
ax2.set_facecolor('#000814')
ax2.set_title('Side View - Gravitational Lensing', color='#ff006e', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('X (Schwarzschild radii)', color='#ff006e', fontsize=10)
ax2.set_ylabel('Y (Schwarzschild radii)', color='#ff006e', fontsize=10)
ax2.tick_params(colors='#ff006e', labelsize=8)
ax2.grid(True, alpha=0.15, color='#ff006e', linestyle=':')

# Panel 3: 3D View
ax3 = fig.add_subplot(gs[:, 2], projection='3d')
ax3.set_xlim(-25, 25)
ax3.set_ylim(-25, 25)
ax3.set_zlim(-25, 25)
ax3.set_facecolor('#000814')
ax3.set_title('3D View - Complete System', color='#ffbe0b', fontsize=14, fontweight='bold', pad=15)
ax3.set_xlabel('X', color='#ffbe0b', fontsize=9)
ax3.set_ylabel('Y', color='#ffbe0b', fontsize=9)
ax3.set_zlabel('Z', color='#ffbe0b', fontsize=9)
ax3.tick_params(colors='#ffbe0b', labelsize=7)
ax3.xaxis.pane.fill = False
ax3.yaxis.pane.fill = False
ax3.zaxis.pane.fill = False
ax3.grid(True, alpha=0.15, color='#ffbe0b')
ax3.xaxis.pane.set_edgecolor('#ffbe0b')
ax3.yaxis.pane.set_edgecolor('#ffbe0b')
ax3.zaxis.pane.set_edgecolor('#ffbe0b')

# Event horizons - dengan glow oranye
circle1 = Circle((0, 0), 1.5, color='#0a0500', ec='#ff6600', linewidth=5, fill=True, zorder=100, alpha=0.9)
circle2 = Circle((0, 0), 1.5, color='#0a0500', ec='#ff6600', linewidth=5, fill=True, zorder=100, alpha=0.9)
ax1.add_patch(circle1)
ax2.add_patch(circle2)

# Inner glow untuk event horizon
inner_glow1 = Circle((0, 0), 2.2, color='none', ec='#ff8800', linewidth=3, alpha=0.4, zorder=98)
inner_glow2 = Circle((0, 0), 2.2, color='none', ec='#ff8800', linewidth=3, alpha=0.4, zorder=98)
ax1.add_patch(inner_glow1)
ax2.add_patch(inner_glow2)

# Photon sphere - bright orange glow
photon_sphere1 = Circle((0, 0), 3, color='none', ec='#ffaa00', linewidth=2.5, linestyle='--', alpha=0.5, zorder=99)
photon_sphere2 = Circle((0, 0), 3, color='none', ec='#ffaa00', linewidth=2.5, linestyle='--', alpha=0.5, zorder=99)
ax1.add_patch(photon_sphere1)
ax2.add_patch(photon_sphere2)

# Scatter plots dengan colormap Interstellar-style (kuning-oranye) - LEBIH TERANG
stars1 = ax1.scatter([], [], s=10, c='white', alpha=0.8, marker='*', zorder=1)
stars2 = ax2.scatter([], [], s=10, c='white', alpha=0.8, marker='*', zorder=1)

# Menggunakan colormap custom: oranye gelap -> oranye cerah -> kuning -> putih terang
from matplotlib.colors import LinearSegmentedColormap
colors_interstellar = ['#2a1500', '#4a2000', '#ff6b00', '#ff8800', '#ffaa00', '#ffd700', '#ffeb99', '#fff9e6', '#ffffff']
n_bins = 256
cmap_interstellar = LinearSegmentedColormap.from_list('interstellar', colors_interstellar, N=n_bins)

scatter1 = ax1.scatter([], [], s=5, c=[], cmap=cmap_interstellar, vmin=0, vmax=2.8, alpha=1.0, zorder=50)
scatter2 = ax2.scatter([], [], s=6, c=[], cmap=cmap_interstellar, vmin=0, vmax=2.8, alpha=0.98, zorder=50)
scatter3 = ax3.scatter([], [], [], s=4, c=[], cmap=cmap_interstellar, vmin=0, vmax=2.8, alpha=0.95)

jets1 = ax1.scatter([], [], s=7, c='#4dd0e1', alpha=1.0, marker='^', edgecolors='#00e5ff', linewidths=0.5, zorder=60)
jets3_pos = ax3.scatter([], [], [], s=6, c='#4dd0e1', alpha=1.0, marker='^', edgecolors='#00e5ff', linewidths=0.3)
jets3_neg = ax3.scatter([], [], [], s=6, c='#26c6da', alpha=1.0, marker='v', edgecolors='#00e5ff', linewidths=0.3)

photons = ax2.scatter([], [], s=2.5, c='#82b1ff', alpha=1.0, zorder=40)

# Info text
info_text = fig.text(0.5, 0.97, '', ha='center', color='#ffbe0b', fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.7', facecolor='#001d3d', edgecolor='#ffbe0b', linewidth=2))

stats_text = fig.text(0.02, 0.02, '', ha='left', va='bottom', color='#ffffff', fontsize=9, 
                     family='monospace', bbox=dict(boxstyle='round,pad=0.6', facecolor='#001d3d', alpha=0.85))

frame_count = 0
last_time = time.time()
fps_list = []

def update(frame):
    global frame_count, last_time
    
    # FPS calculation
    current_time = time.time()
    fps = 1.0 / (current_time - last_time + 1e-6)
    fps_list.append(fps)
    if len(fps_list) > 30:
        fps_list.pop(0)
    avg_fps = np.mean(fps_list)
    last_time = current_time
    
    # Update simulasi
    dt = 8e-7 * bh.rs / c
    for _ in range(2):
        bh.update(dt)
    
    # Get data
    rs = bh.rs
    x_norm = bh.x / rs
    y_norm = bh.y / rs
    z_norm = bh.z / rs
    
    # Update stars
    stars1.set_offsets(np.c_[bh.sx/rs, bh.sy/rs])
    stars2.set_offsets(np.c_[bh.sx/rs, bh.sy/rs])
    
    # Update particles
    scatter1.set_offsets(np.c_[x_norm, y_norm])
    scatter1.set_array(bh.temperature)
    
    scatter2.set_offsets(np.c_[x_norm, z_norm])
    scatter2.set_array(bh.temperature)
    
    scatter3._offsets3d = (x_norm, y_norm, z_norm)
    scatter3.set_array(bh.temperature)
    
    # Update jets
    jets1.set_offsets(np.c_[bh.jx/rs, bh.jy/rs])
    
    mask_pos = bh.jz > 0
    jets3_pos._offsets3d = (bh.jx[mask_pos]/rs, bh.jy[mask_pos]/rs, bh.jz[mask_pos]/rs)
    jets3_neg._offsets3d = (bh.jx[~mask_pos]/rs, bh.jy[~mask_pos]/rs, bh.jz[~mask_pos]/rs)
    
    # Update photons
    photons.set_offsets(np.c_[bh.px/rs, bh.py/rs])
    
    # Rotate 3D view
    ax3.view_init(elev=20, azim=frame_count * 0.4)
    
    # Update info
    frame_count += 1
    time_norm = bh.time * c / rs
    info_text.set_text(f'🌌 GARGANTUA (Interstellar) | Frame: {frame_count} | Time: {time_norm:.2f} τ | FPS: {avg_fps:.1f}')
    
    # Stats
    stats = f"PARTICLES: {bh.n_particles} | JETS: {bh.n_jets} | PHOTONS: {bh.n_photons}\n"
    stats += f"Rs = {rs:.2e} m | Mass = {bh.M/M_sun:.1f} M☉\n"
    stats += f"Mode: CPU Optimized (NumPy Vectorized) ⚡"
    stats_text.set_text(stats)

print("\n🚀 Memulai animasi...")
print("⚡ Optimized untuk performa maksimal di CPU")
print("📊 Close window untuk menghentikan\n")

anim = FuncAnimation(fig, update, frames=None, interval=20, blit=False, cache_frame_data=False)

plt.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.08, wspace=0.25, hspace=0.3)
plt.show()

print("\n" + "=" * 65)
print("   ✓ Simulasi selesai!")
print("=" * 65)