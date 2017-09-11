from kivy.tests.common import GraphicUnitTest, UnitTestTouch

from kivy.lang import Builder
from kivy.base import EventLoop
from kivy.modules import inspector
from kivy.factory import Factory


KV = '''
#:import Factory kivy.factory.Factory

<InspectorTestModal@ModalView>:
    size_hint: 0.5, 0.5

<FirstModal@InspectorTestModal>:
    Button:
        id: firstmodal
        text: 'first modal'
        on_release: Factory.SecondModal().open()

<SecondModal@InspectorTestModal>:
    Button:
        id: secondmodal
        text: 'second modal'
        on_release: Factory.ThirdModal().open()

<ThirdModal@InspectorTestModal>:
    Button:
        id: thirdmodal
        text: 'third modal'

BoxLayout:
    Button:
        id: highlight
        text: 'highlight'
    Button:
        id: popup
        text: 'popup'
        on_release: Factory.FirstModal().open()
    Button:
        id: tri_popup
        text: '3 popups'
        on_release: Factory.FirstModal().open()
    Button:
        id: dummy
        text: 'dummy'
'''


class InspectorTestCase(GraphicUnitTest):
    framecount = 0

    def clean_garbage(self, *args):
        for child in self._win.children[:]:
            self._win.remove_widget(child)
        self.advance_frames(5)

    def test_activate_deactivate_bottom(self, *args):
        EventLoop.ensure_window()
        self._win = EventLoop.window

        self.clean_garbage()

        # build the widget tree & add Window as the main EL
        self.root = Builder.load_string(KV)
        self.render(self.root)
        self.assertLess(len(self._win.children), 2)

        # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(2)
        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        ins.activated = True
        ins.inspect_enabled = True
        self.assertTrue(ins.at_bottom)

        # by default is Inspector appended as the first child
        # to the window and positioned at the bottom
        self.assertEqual(self._win.children[0], ins)
        self.advance_frames(1)
        self.assertLess(ins.layout.pos[1], self._win.height / 2.0)

        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False
        self.render(self.root)
        self.advance_frames(1)

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)
        self.render(self.root)

    def test_activate_deactivate_top(self, *args):
        EventLoop.ensure_window()
        self._win = EventLoop.window

        self.clean_garbage()

        # build the widget tree & add Window as the main EL
        self.root = Builder.load_string(KV)
        self.render(self.root)
        self.assertLess(len(self._win.children), 2)

        # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(2)
        # pull the Inspector drawer from top
        ins = self.root.inspector
        ins.at_bottom = False
        ins.activated = True
        ins.inspect_enabled = True
        self.assertFalse(ins.at_bottom)

        # by default is Inspector appended as the first child
        # to the window & we move it to the top
        self.assertEqual(self._win.children[0], ins)
        ins.toggle_position(self.root.ids.dummy)
        self.advance_frames(20)  # drawer is moving
        self.assertGreater(ins.layout.pos[1], self._win.height / 2.0)

        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False
        self.render(self.root)
        self.advance_frames(1)

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)
        self.render(self.root)

    def test_widget_button(self, *args):
        EventLoop.ensure_window()
        self._win = EventLoop.window

        self.clean_garbage()

        # build the widget tree & add Window as the main EL
        self.root = Builder.load_string(KV)
        self.render(self.root)
        self.assertLess(len(self._win.children), 2)

        # checked widget
        highlight = self.root.ids.highlight
        highlight_exp = self.root.ids.highlight.text

        # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(2)
        # pull the Inspector drawer from bottom
        ins = self.root.inspector
        ins.activated = True
        ins.inspect_enabled = True
        self.assertTrue(ins.at_bottom)

        # touch button center
        touch = UnitTestTouch(*highlight.center)
        touch.touch_down()
        # open Inspector properties
        ins.show_widget_info()
        self.advance_frames(2)

        # check if the button is selected
        # stored instance
        self.assertEqual(ins.widget.text, highlight_exp)
        # data in properties
        for node in ins.treeview.iterate_all_nodes():
            lkey = getattr(node.ids, 'lkey', None)
            if not lkey:
                continue
            if lkey.text == 'text':
                ltext = node.ids.ltext
                # slice because the string is displayed with quotes
                self.assertEqual(ltext.text[1:-1], highlight_exp)
                break

        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False
        self.render(self.root)
        self.advance_frames(1)

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)
        self.render(self.root)

    def test_widget_popup(self, *args):
        EventLoop.ensure_window()
        self._win = EventLoop.window

        self.clean_garbage()

        # build the widget tree & add Window as the main EL
        self.root = Builder.load_string(KV)
        self.render(self.root)
        self.assertLess(len(self._win.children), 2)

        # checked widget
        popup = self.root.ids.popup
        popup_exp = self.root.ids.popup.text

        # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)
        # pull the Inspector drawer from bottom,
        # but don't inspect yet!
        ins = self.root.inspector
        ins.inspect_enabled = False
        ins.activated = True
        self.assertTrue(ins.at_bottom)

        # touch button center to open the popup
        touch = UnitTestTouch(*popup.center)
        touch.touch_down()
        touch.touch_up()
        self.advance_frames(1)

        # start inspecting
        ins.inspect_enabled = True
        self.advance_frames(1)

        # inspect FirstModal's button
        touch.touch_down()
        touch.touch_up()
        self.advance_frames(1)

        # open Inspector properties
        ins.show_widget_info()
        self.advance_frames(2)

        # check if the popup is selected
        # stored instance
        self.assertIsInstance(ins.widget, Factory.Button)
        self.assertIsInstance(ins.widget.parent, Factory.FirstModal)
        # check with new Popup instance if the properties match
        temp_popup = Factory.FirstModal()
        temp_popup_exp = temp_popup.ids.firstmodal.text
        self.assertEqual(ins.widget.text, temp_popup_exp)
        # data in properties
        for node in ins.treeview.iterate_all_nodes():
            lkey = getattr(node.ids, 'lkey', None)
            if not lkey:
                continue
            if lkey.text == 'text':
                ltext = node.ids.ltext
                # slice because the string is displayed with quotes
                self.assertEqual(ltext.text[1:-1], temp_popup_exp)
                break
        del temp_popup

        # close popup
        ins.inspect_enabled = False
        touch = UnitTestTouch(0, 0)
        touch.touch_down()
        touch.touch_up()
        self.advance_frames(10)

        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False
        self.render(self.root)
        self.advance_frames(10)

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)
        self.render(self.root)

    def _test_widget_multipopup(self, *args):
        # still not complete

        EventLoop.ensure_window()
        self._win = EventLoop.window

        self.clean_garbage()

        # build the widget tree & add Window as the main EL
        self.root = Builder.load_string(KV)
        self.render(self.root)
        self.assertLess(len(self._win.children), 2)

        # checked widget
        popup = self.root.ids.popup
        popup_exp = self.root.ids.popup.text

        # activate inspector with root as ctx
        inspector.start(self._win, self.root)
        self.advance_frames(1)
        # pull the Inspector drawer from bottom,
        # but don't inspect yet!
        ins = self.root.inspector
        ins.inspect_enabled = False
        ins.activated = True
        self.assertTrue(ins.at_bottom)

        # touch button center to open the popup
        touch = UnitTestTouch(*popup.center)
        touch.touch_down()
        touch.touch_up()
        self.advance_frames(1)

        # touch Window center to open
        # the second and the third popup
        touch = UnitTestTouch(
            self._win.width / 2.0,
            self._win.height / 2.0
        )
        for i in range(2):
            touch.touch_down()
            touch.touch_up()
            self.advance_frames(1)

        # start inspecting
        ins.inspect_enabled = True
        self.advance_frames(1)

        # inspect ThirdModal's button
        touch.touch_down()
        touch.touch_up()
        self.advance_frames(1)

        # open Inspector properties
        ins.show_widget_info()
        self.advance_frames(2)

        # fixed order, first opened - last closed
        modals = (
            Factory.ThirdModal,
            Factory.SecondModal,
            Factory.FirstModal
        )
        for mod in modals:
            print(mod)
            # check if the popup is selected
            # stored instance
            self.assertIsInstance(ins.widget, Factory.Button)
            self.assertIsInstance(ins.widget.parent, mod)
            # check with new Popup instance if the properties match
            temp_popup = mod()
            temp_popup_exp = temp_popup.ids[
                list(temp_popup.ids.keys())[0]
            ].text
            self.assertEqual(ins.widget.text, temp_popup_exp)
            # data in properties
            for node in ins.treeview.iterate_all_nodes():
                lkey = getattr(node.ids, 'lkey', None)
                if not lkey:
                    continue
                if lkey.text == 'text':
                    ltext = node.ids.ltext
                    # slice because the string is displayed with quotes
                    self.assertEqual(ltext.text[1:-1], temp_popup_exp)
                    break
            del temp_popup
            self.advance_frames(100)
            ins.widget.parent.dismiss()
            self.advance_frames(100)

        # close popup
        ins.inspect_enabled = False
        touch = UnitTestTouch(0, 0)
        touch.touch_down()
        touch.touch_up()
        self.advance_frames(10)

        # close Inspector
        ins.inspect_enabled = False
        ins.activated = False
        self.render(self.root)
        self.advance_frames(10)

        # stop Inspector completely
        inspector.stop(self._win, self.root)
        self.assertLess(len(self._win.children), 2)
        self.render(self.root)


if __name__ == '__main__':
    import unittest
    unittest.main()
