

import cocos
import cocos.particle_systems as ps
class MainLayer(cocos.layer.Layer):
        def __init__(self):
                super(MainLayer, self).__init__()
                particles = ps.Fireworks(fallback = False)
                particles.angle = 180
                particles.size = 3
                particles.position = (320, 240)
                self.add(particles)

if __name__ == '__main__':
        cocos.director.director.init(caption='Othello', width=75 * 8, height=75 * 8)

        scene = cocos.scene.Scene()
        scene.add(MainLayer())

        cocos.director.director.run(scene)
