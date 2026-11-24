#!/usr/bin/env bash

# Collect a read-only environment report for the course GPU VM.
# The only file created by this script is the report itself.

set -u

timestamp="$(date +%Y%m%d-%H%M%S)"
report_path="${1:-environment_report_${timestamp}.txt}"

section() {
  printf '\n===== %s =====\n' "$1"
}

run_if_available() {
  local command_name="$1"
  shift
  if command -v "$command_name" >/dev/null 2>&1; then
    "$@" 2>&1 || true
  else
    printf '%s: NOT FOUND\n' "$command_name"
  fi
}

collect_report() {
  section "REPORT METADATA"
  printf 'generated_at=%s\n' "$(date --iso-8601=seconds 2>/dev/null || date)"
  printf 'user=%s\n' "$(id -un)"
  printf 'home=%s\n' "$HOME"
  printf 'hostname=%s\n' "$(hostname)"
  printf 'desktop_session=%s\n' "${XDG_CURRENT_DESKTOP:-unknown}"
  printf 'display=%s\n' "${DISPLAY:-unset}"

  section "OPERATING SYSTEM"
  if [[ -r /etc/os-release ]]; then
    cat /etc/os-release
  fi
  uname -a

  section "CPU"
  run_if_available lscpu lscpu

  section "MEMORY"
  run_if_available free free -h

  section "FILESYSTEM"
  run_if_available df df -hT

  section "NVIDIA GPU"
  run_if_available nvidia-smi nvidia-smi
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,driver_version,memory.total,memory.free,compute_cap --format=csv,noheader 2>&1 || true
  fi

  section "ISAAC SIM CANDIDATES"
  for candidate in \
    /isaac-sim/isaac-sim.sh \
    /isaacsim/isaac-sim.sh \
    /opt/isaacsim/isaac-sim.sh \
    "$HOME/isaac-sim/isaac-sim.sh" \
    "$HOME/isaacsim/isaac-sim.sh"; do
    if [[ -e "$candidate" ]]; then
      ls -l "$candidate"
    fi
  done

  desktop_dir=""
  if command -v xdg-user-dir >/dev/null 2>&1; then
    desktop_dir="$(xdg-user-dir DESKTOP 2>/dev/null || true)"
  fi
  for candidate_dir in "$desktop_dir" "$HOME/Desktop" "$HOME/桌面"; do
    if [[ -n "$candidate_dir" && -d "$candidate_dir" ]]; then
      printf '\nDesktop directory: %s\n' "$candidate_dir"
      find "$candidate_dir" -maxdepth 1 -type f -printf '%f -> %p\n' 2>/dev/null | sort
      while IFS= read -r script; do
        printf '\n--- script preview: %s ---\n' "$script"
        sed -n '1,80p' "$script" 2>/dev/null || true
      done < <(find "$candidate_dir" -maxdepth 1 -type f \( \
        -name '*isaac*.sh' -o -name 'start*.sh' -o \
        -name '*isaac*.desktop' -o -name 'start*.desktop' \
      \) 2>/dev/null)
    fi
  done

  section "ROS 2"
  printf 'ROS_DISTRO=%s\n' "${ROS_DISTRO:-unset}"
  printf 'ROS_DOMAIN_ID=%s\n' "${ROS_DOMAIN_ID:-unset}"
  printf 'RMW_IMPLEMENTATION=%s\n' "${RMW_IMPLEMENTATION:-unset}"
  if [[ -d /opt/ros ]]; then
    find /opt/ros -maxdepth 2 -name setup.bash -print 2>/dev/null | sort
  else
    printf '/opt/ros: NOT FOUND\n'
  fi
  if command -v ros2 >/dev/null 2>&1; then
    command -v ros2
    ros2 pkg prefix nav2_bringup 2>&1 || true
    ros2 pkg prefix navigation2 2>&1 || true
    ros2 pkg list 2>/dev/null | grep -E '^(nav2_|navigation2$|rosbridge|isaac)' | sort || true
  else
    printf 'ros2: NOT FOUND IN CURRENT SHELL\n'
  fi

  section "DEVELOPMENT TOOLS"
  run_if_available git git --version
  run_if_available python3 python3 --version
  run_if_available pip3 pip3 --version
  run_if_available cmake cmake --version
  run_if_available colcon colcon version-check

  section "NETWORK CONFIGURATION"
  run_if_available ip ip -brief address
  run_if_available ip ip route

  section "PERSISTENCE MARKER"
  marker="$HOME/.warehouse_robot_vm_persistence_check"
  if [[ -f "$marker" ]]; then
    printf 'FOUND: %s\n' "$marker"
    cat "$marker"
  else
    printf 'NOT FOUND: %s\n' "$marker"
    printf 'Create it after confirming the home directory is appropriate; see environment/README.md.\n'
  fi
}

collect_report | tee "$report_path"
printf '\nReport saved to: %s\n' "$(readlink -f "$report_path" 2>/dev/null || printf '%s' "$report_path")"
