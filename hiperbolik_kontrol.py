import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn
import numpy as np
import math


class AvciIHA(Node):
    def __init__(self):
        super().__init__('avci_iha_node')

        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.subscriber_avci = self.create_subscription(Pose, 'turtle1/pose', self.avci_pose_cb, 10)
        self.subscriber_dusman = self.create_subscription(Pose, 'turtle2/pose', self.dusman_pose_cb, 10)

        self.avci_pose = None
        self.dusman_pose = None
        self.a = 2.0  # Poster: Hiperbol parametresi [cite: 12]
        self.b = 1.5
        self.hedef_vuruldu = False
        self.mod = "TAKIP"

        # Safe Zone parametreleri
        self.merkez_x = 5.5
        self.merkez_y = 5.5
        self.guvenlik_yaricap = 3.0

        # Hedefi (turtle2) oluşturma servisi
        self.spawn_client = self.create_client(Spawn, 'spawn')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Simülasyon servisinin açılması bekleniyor...')

        self.dusman_yarat()
        self.timer = self.create_timer(0.1, self.kontrol_dongusu)

    def dusman_yarat(self):
        request = Spawn.Request()
        request.x = 8.5
        request.y = 8.5
        request.name = 'turtle2'  # Hedef kaplumbağa ismi
        self.spawn_client.call_async(request)

    def avci_pose_cb(self, msg):
        self.avci_pose = msg

    def dusman_pose_cb(self, msg):
        self.dusman_pose = msg

    def delta_analizi(self):
        # Poster: Delta = 4a^2b^2(n^2 + b^2 - a^2m^2) [cite: 19, 58]
        if self.dusman_pose is None: return None
        m = math.tan(self.dusman_pose.theta)
        n = self.dusman_pose.y - m * self.dusman_pose.x
        delta = 4 * (self.a ** 2) * (self.b ** 2) * (n ** 2 + self.b ** 2 - (self.a ** 2) * (m ** 2))
        return delta

    def kontrol_dongusu(self):
        # Eğer hedef henüz oluşmadıysa veya vurulduysa işlem yapma
        if self.avci_pose is None or self.dusman_pose is None or self.hedef_vuruldu:
            return

        msg = Twist()
        delta = self.delta_analizi()

        # Mesafe ve Açı Hesaplama
        dx = self.dusman_pose.x - self.avci_pose.x
        dy = self.dusman_pose.y - self.avci_pose.y
        mesafe = math.sqrt(dx ** 2 + dy ** 2)
        hedef_aci = math.atan2(dy, dx)

        # Açı Normalizasyonu (Düz gitme sorununu çözer)
        aci_farki = hedef_aci - self.avci_pose.theta
        while aci_farki > math.pi: aci_farki -= 2.0 * math.pi
        while aci_farki < -math.pi: aci_farki += 2.0 * math.pi

        # Poster: Güvenli-Kritik-Tehlikeli Bölge Analizi
        mesafe_merkez = math.sqrt((self.dusman_pose.x - self.merkez_x) ** 2 + (self.dusman_pose.y - self.merkez_y) ** 2)

        if mesafe_merkez < self.guvenlik_yaricap:
            self.mod = "SAVUNMA"  # Kritik müdahale bölgesi [cite: 29]
            hiz_kat_sayisi = 3.0
        elif delta is not None and delta > 0:
            self.mod = "RISK"  # Delta > 0 ise iletişim kesilecek tahmini [cite: 61]
            hiz_kat_sayisi = 2.2
        else:
            self.mod = "TAKIP"
            hiz_kat_sayisi = 1.5

        if mesafe > 0.6:
            # Hiperbolik yaklaşma hızı [cite: 106]
            msg.linear.x = hiz_kat_sayisi * np.tanh(mesafe)
            msg.angular.z = 6.0 * aci_farki
            self.publisher_.publish(msg)
        else:
            self.hedef_vuruldu = True
            self.get_logger().info("HEDEF ETKİSİZ HALE GETİRİLDİ!")  # Müdahale Başarılı [cite: 64]


def main():
    rclpy.init()
    node = AvciIHA()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()