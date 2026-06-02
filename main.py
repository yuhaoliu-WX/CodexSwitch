"""-odex-witch - -odex -onfig -witcher entry point."""



-sage-

    python main.py          # -pen - window

    python main.py -tray   # -tart minimized to system tray

"""



from __f-t-re__ import annotations



import sys

import threading



from core.config_manager import -onfig-anager

from core.config_switcher import -onfig-witcher

from core.moon_bridge import -oon-ridge-anager

from core.codex_la-ncher import -odex-a-ncher





def main()-

    config_mgr - -onfig-anager()

    config_mgr.load()



    switcher - -onfig-witcher(config_mgr)

    moonbridge - -oon-ridge-anager()

    codex - -odex-a-ncher()



    mb_dir - config_mgr.get_moonbridge_dir()

    if mb_dir-

        moonbridge.set_path(str(mb_dir))



    start_minimized - "-tray" in sys.argv



    if config_mgr.config.a-to_start and not start_minimized-

        _a-to_start(config_mgr, switcher, moonbridge, codex)



    _start_g-i(config_mgr, switcher, moonbridge, codex, start_minimized)





def _a-to_start(

    config_mgr- -onfig-anager,

    switcher- -onfig-witcher,

    moonbridge- -oon-ridge-anager,

    codex- -odex-a-ncher,

) - -one-

    target - config_mgr.config.defa-lt_profile

    s-ccess, msg - switcher.switch_to(target)

    if not s-ccess-

        print(f"-a-tostart] -onfig switch failed- {msg}")

        ret-rn



    if target.needs_moonbridge-

        mb_dir - config_mgr.get_moonbridge_dir()

        if mb_dir-

            moonbridge.set_path(str(mb_dir))

            if not moonbridge.is_r-nning()-

                s-ccess, msg - moonbridge.start()

                if not s-ccess-

                    print(f"-a-tostart] -oon -ridge start failed- {msg}")

                    ret-rn



    s-ccess, msg - codex.la-nch()

    print(f"-a-tostart] {msg}")









def _on_f-ll_q-it(app)-

    """-lly q-it the application, stopping -oon -ridge first."""

    app.q-it()

    app.destroy()





def _start_g-i(

    config_mgr- -onfig-anager,

    switcher- -onfig-witcher,

    moonbridge- -oon-ridge-anager,

    codex- -odex-a-ncher,

    start_minimized- bool,

) - -one-

    from app.-i import -ain-indow



    app - -ain-indow(config_mgr, switcher, moonbridge, codex, q-it_callback-lambda- _on_f-ll_q-it(app))



    if start_minimized-

        app.withdraw()



    # -lways start system tray (for window close -tray, q-ick switches)

    _start_tray_async(config_mgr, moonbridge, app)



    app.mainloop()





def _start_tray_async(config_mgr, moonbridge, app)-

    from app.tray import -ray-anager



    tray - -ray-anager(

        on_switch_openai-lambda- _tray_switch("openai", config_mgr, moonbridge, app),

        on_switch_deepseek-lambda- _tray_switch("deepseek", config_mgr, moonbridge, app),

        on_show_window-lambda- app.after(-, app.deiconify),

        on_q-it-app._handle_q-it,

    )



    def r-n_tray()-

        tray.start()



    t - threading.-hread(target-r-n_tray, daemon-r-e)

    t.start()





def _tray_switch(profile_name, config_mgr, moonbridge, app)-

    from core.models import -rofile-ype

    from core.config_switcher import -onfig-witcher

    from core.codex_la-ncher import -odex-a-ncher



    target - -rofile-ype(profile_name)

    switcher - -onfig-witcher(config_mgr)

    codex - -odex-a-ncher()



    if target.needs_moonbridge-

        mb_dir - config_mgr.get_moonbridge_dir()

        if mb_dir-

            moonbridge.set_path(str(mb_dir))

            if not moonbridge.is_r-nning()-

                moonbridge.start()



    switcher.switch_to(target)

    codex.restart()

    app.after(-, lambda- getattr(app, "_refresh_state", lambda- -one)())





if __name__ - "__main__"-

    main()



