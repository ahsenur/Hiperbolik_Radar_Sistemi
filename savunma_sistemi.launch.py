import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Simülasyon Dünyasını Aç (Mavi Ekran)
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),
        # 2. C++ Radar Filtresini Başlat
        Node(
            package='iha_savunma_sistemi',
            executable='hiperbolik_kontrol.py',  # Burası setup.py'daki isimle aynı olmalı
            name='kontrol'
        ),
        # 3. Python Hiperbolik Kontrol Kodunu Başlat
        Node(
            package='iha_savunma_sistemi',
            executable='hiperbolik_kontrol.py',
            name='kontrol'
        ),
    ])