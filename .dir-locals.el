;; Pony mode config for the megacorp project
((nil . ;; This applies these settings regardless of major mode

      ((pony-settings (make-pony-project
                       :python "/str/development/projects/jwind/osbb/product/venv/bin/python3.5"
                       :pythonpath "/str/development/projects/jwind/osbb/product/osbb/"
                       :settings "settings"
                       :appsdir "/str/development/projects/jwind/osbb/product/osbb/")
                      ))))
