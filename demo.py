from manimlib.imports import *


class Stop(Exception):
    def __init__(self, last_animations):
        self.animations = last_animations


class Main(Scene):
    CONFIG={
        "camera_config": {
            "background_image": r"media/bgg.png",
        },
    }
    current_month = 1

    @property
    def data(self):
        return [
            ['china.jpeg', RED, *range(100, 100+1*12, 1)],
            ['a.jpeg', YELLOW, *range(90, 90+15*12, 15)],
            ['b.jpeg', PINK, *range(80, 80+10*12, 10)],
            ['c.jpeg', GREEN, *range(70, 70+25*12, 25)],
            ['d.jpeg', GRAY, *range(60, 60+4105*12, 10)],
        ]

    def construct(self):
        self.add_sound('audio.mp3')
        title = TextMobject(
            "{\\tiny 全球主要国家新冠确诊变化}",
        ).to_edge(UL)

        time_bar = NumberLine(
            x_min=1,
            x_max=13,
            numbers_with_elongated_ticks=[1],
            include_numbers=True,
            include_tip=True,
            tick_size=0.05,
            number_scale_val=0.3,
            line_to_number_buff=SMALL_BUFF,
            tip_length=0.1,
        )
        time_bar.to_edge(DL).shift(DOWN*0.35)

        cursor = Triangle(color=RED).set_fill(color=RED, opacity=0.5)
        cursor.set_width(0.1, stretch=False).set_height(0.1, stretch=False)
        cursor.rotate(180*DEGREES).to_edge(DL)
        month_label = Integer(self.current_month).to_edge(RIGHT)

        self.add(title, time_bar, cursor, month_label)
        group = self.add_rectangle_group()
        self.wait(0.5)

        # 移动游标，计算并播放动画
        while True:
            try:
                self.play(*self.make_animations(month_label, cursor, group), rate_func=linear)
            except Stop as error:
                self.play(*error.animations)
                break

    def add_rectangle_group(self):
        max_numbers = [max(x) for x in zip(*[item[2:] for item in self.data])]
        print(f'max_numbers:{max_numbers}')
        
        standard_height = 0.5
        rectangles = []

        # 第一个场景
        for item in self.data:
            country = item[0]
            color = item[1]
            first_number = item[2]

            rectangle = Rectangle(color=color, width=self.get_rectangle_width(first_number, max_numbers[0]), height=standard_height)
            rectangle.set_fill(color=color, opacity=0.5)
            rectangle.name = country
            rectangle.data = item[2:]
            rectangle.max_numbers = max_numbers
            
            flag = ImageMobject(f'media/{country}', height=standard_height)
            flag.master = rectangle
            flag.add_updater(lambda x: x.next_to(x.master, buff=0.1))

            number = Integer(first_number).scale(0.7)
            number.master = flag
            number.add_updater(lambda x: x.next_to(x.master, buff=0.1))
            rectangle.number = number

            rectangles.append(rectangle)
            self.add(rectangle, flag, number)

        # 组合排序
        group = VGroup(*rectangles).sort(submob_func=lambda x: -x.number.get_value()).arrange(DOWN)

        for rectangle in rectangles:
            rectangle.to_edge(LEFT)

        return group

    @staticmethod
    def get_rectangle_width(number, max_number):
        max_width = 10
        return number*max_width/max_number

    def make_animations(self, month_label, cursor, group):
        old_value = self.current_month
        print(f'old value:{old_value}')

        target = cursor.copy().shift(RIGHT)
        target_value = int(target.get_last_point()[0] + 7.6)
        print(f'target value:{target_value}')

        # always move cursor
        animations = [Transform(cursor, target)]
        
        # 停止条件
        if target_value > 12:
            raise Stop(animations)

        if old_value != target_value:
            self.current_month = target_value

            print(f'render anim for month label to {target_value}')
            animations.append(Transform(month_label, month_label.copy().set_value(target_value)))

            print(f'render anim for rectangle to {target_value}')
            animations += self.make_rectangle_group_animations(target_value, group)
            
        return animations

    def make_rectangle_group_animations(self, month, group):
        index = month - 1
        animations = []
        target_group = group.copy()

        for rectangle in target_group.submobjects:
            value = rectangle.data[index]
            rectangle.number = rectangle.number.copy().set_value(value)

            width = self.get_rectangle_width(value, rectangle.max_numbers[index])
            rectangle.set_width(width, stretch=True)

        target_group.sort(submob_func=lambda x: -x.number.get_value()).arrange(DOWN)

        for rectangle in target_group.submobjects:
            rectangle.to_edge(LEFT)

        target_map = {x.name: x for x in target_group.submobjects}

        for rectangle in group.submobjects:
            target = target_map[rectangle.name]
            animations += [
                Transform(rectangle, target),
                Transform(rectangle.number, target.number),
            ]

        return animations
